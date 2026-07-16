const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function requestJson(path) {
  const response = await fetch(`${API_URL}${path}`);

  if (!response.ok) {
    let detail = "";
    try {
      const body = await response.json();
      detail = body.detail || "";
    } catch {
      detail = "";
    }

    throw new Error(detail || `Error ${response.status} al consultar ${path}.`);
  }

  return response.json();
}

async function settle(name, path) {
  try {
    return [name, { data: await requestJson(path), error: null }];
  } catch (error) {
    return [name, { data: null, error: error.message }];
  }
}

export async function fetchMonitoringOverview() {
  const responses = await Promise.all([
    settle("readiness", "/health/ready"),
    settle("model", "/model/info"),
    settle("drift", "/monitoring/drift"),
    settle("feedback", "/feedback/summary")
  ]);

  return Object.fromEntries(responses);
}
