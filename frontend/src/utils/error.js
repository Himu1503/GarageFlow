export function getErrorMessage(error, fallback = "Something went wrong") {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object") return item.msg || JSON.stringify(item);
        return "";
      })
      .filter(Boolean);
    return messages.length ? messages.join(", ") : fallback;
  }

  if (detail && typeof detail === "object") {
    return detail.msg || fallback;
  }

  if (typeof error?.message === "string" && error.message) return error.message;
  return fallback;
}
