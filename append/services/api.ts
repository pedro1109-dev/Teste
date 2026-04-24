const API_URL = 'http://127.0.0.1:8000';

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const controller = new AbortController();

  const timeout = setTimeout(() => {
    controller.abort();
  }, 30000);

  try {
    console.log('CHAMANDO API:', `${API_URL}${endpoint}`);

    // 🔥 Detecta se é FormData (upload de arquivo)
    const isFormData = options.body instanceof FormData;

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: isFormData
        ? {
            // NÃO define Content-Type (o fetch faz sozinho)
            ...(options.headers || {}),
          }
        : {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
          },
    });

    clearTimeout(timeout);

    const text = await response.text();

    let data: any = null;

    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = text;
    }

    if (!response.ok) {
      throw {
        status: response.status,
        data,
        message:
          data?.detail ||
          data?.message ||
          `Erro na API: ${response.status}`,
      };
    }

    return data;
  } catch (error: any) {
    clearTimeout(timeout);

    if (error.name === 'AbortError') {
      throw {
        message:
          'A API demorou muito para responder. Verifique se ela está rodando.',
      };
    }

    throw error;
  }
}