const BASE_API_URL = '.'
const APPS_URL = `${BASE_API_URL}/apps.json`

export const apiRequest = async (requestMethod, args) => {
  const promise = args.length === 0 ? requestMethod() : requestMethod(...args)
  const response = await promise.catch(() => null)
  const json = await parseResponse(response)
  const requestError = await handleRequestError(response, json)
  return { json, requestError }
}

const parseResponse = async response => {
  try {
    return await response.json()
  } catch (e) {
    return null
  }
}

const handleRequestError = async (response, json) => {
  if (!json)
    return {
      status: 500,
      type: 'server',
    }
  if (response && response.status < 400) return null
  return {
    status: response.status,
    type: response.status < 500 ? 'request' : 'server',
  }
}

const apiGetRequest = async url =>
  await fetch(url, {
    headers: new Headers({
      'Content-Type': 'application/json',
    }),
    method: 'get',
  })

export const apiGetApps = () => apiGetRequest(APPS_URL)
