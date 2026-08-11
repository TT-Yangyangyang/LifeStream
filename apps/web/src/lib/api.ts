export type ApiCaptureVisibility = "private" | "friends";

export type ApiCapture = {
  id: string;
  workspace_id: string;
  content: string;
  occurred_at: string;
  visibility: ApiCaptureVisibility;
  allow_ai_processing: boolean;
  created_at: string;
  updated_at: string;
};

type StreamResponse = {
  items: ApiCapture[];
  next_cursor: string | null;
};

type CreateCaptureInput = {
  content: string;
  visibility: ApiCaptureVisibility;
  allow_ai_processing: boolean;
};

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

/** 读取当前本地开发环境所需的 API 配置。 */
function getApiConfig(): {
  baseUrl: string;
  workspaceId: string;
} {
  // 1.1 从 Next.js 公开环境变量中读取 API 地址和当前工作区。
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");
  const workspaceId = process.env.NEXT_PUBLIC_WORKSPACE_ID;

  // 2.1 缺少配置时阻止页面静默请求错误地址。
  if (!baseUrl || !workspaceId) {
    throw new Error("缺少前端 API 配置，请检查 apps/web/.env.local。");
  }

  // 3.1 返回后续请求共用的基础配置。
  return { baseUrl, workspaceId };
}

/** 执行 JSON API 请求，并统一处理非成功响应。 */
async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  // 1.1 读取当前 API 地址。
  const { baseUrl } = getApiConfig();

  // 2.1 发起请求并声明 JSON 内容类型。
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  // 3.1 对失败响应提取服务端错误信息。
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail =
      typeof body?.detail === "string"
        ? body.detail
        : "请求失败，请稍后重试。";

    throw new ApiError(response.status, detail);
  }

  // 4.1 返回经过 FastAPI 校验后的 JSON 数据。
  return response.json() as Promise<T>;
}

/** 读取当前生活空间中按时间倒序排列的真实记录。 */
export async function getStream(limit = 20): Promise<ApiCapture[]> {
  // 1.1 获取当前工作区，保证请求始终带有工作区边界。
  const { workspaceId } = getApiConfig();

  // 2.1 请求并返回时间流中的真实 Capture 列表。
  const response = await request<StreamResponse>(
    `/v1/workspaces/${workspaceId}/stream?limit=${limit}`,
  );

  return response.items;
}

/** 在当前生活空间中创建一条原始生活记录。 */
export async function createCapture(
  input: CreateCaptureInput,
): Promise<ApiCapture> {
  // 1.1 获取当前工作区。
  const { workspaceId } = getApiConfig();

  // 2.1 将已填写的记录内容写入后端事实层。
  return request<ApiCapture>(
    `/v1/workspaces/${workspaceId}/captures`,
    {
      method: "POST",
      body: JSON.stringify(input),
    },
  );
}