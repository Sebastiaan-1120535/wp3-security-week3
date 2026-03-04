
/**
 * @typedef {Object} ApiError
 * @property {boolean} success - Indicates if the request was successful
 * @property {number} status - HTTP status code
 * @property {string} statusText - HTTP status text
 * @property {string} message - Error message
 */

/**
 * @typedef {Object} ApiResponse
 * @property {Object|string|null} data - The response data, can be an object or string
 * @property {ApiError|null} error - The error object if an error occurred, otherwise null
 */

/**
 * @typedef {Object} ApiOptions 
 * @property {string} [extends] - Additional path to append to the base URL
 * @property {Object} [body] - Request body object that will be JSON stringified
 * @property {string} [method] - HTTP method (GET, POST, etc.)
 * @property {Object} [headers] - Request headers
 * @property {AbortSignal} [signal] - AbortSignal to abort the request
 * 
 */

/**
 * @typedef {Object} ApiGetResponse
 * @property {Object|string|null} data - The response data, can be an object or string
 * @property {ApiError|null} error - The error object if an error occurred, otherwise null
 * @property {function(): Promise<ApiResponse>} refresh - Function to refresh the GET request
 */

/**
 * Handles async promise responses and catches errors.
 *
 * @async
 * @param {Promise<Response>} promise - A fetch promise that resolves to a Response object
 * @returns {Promise<ApiResponse>} ApiResponse object containing data and error
 *
 * @description
 * This function wraps a fetch promise and:
 * - Returns an error object if the response is not ok (status not in 200-299 range)
 * - Parses JSON responses when Content-Type is application/json
 * - Returns text content when Content-Type is text/html
 */
const catcher = async (promise) => {
    await new Promise((resolve) => setTimeout(resolve, 500));

    const response = await promise

    if (!response.ok) return {
        data: null,
        error: {
            success: response.ok,
            status: response.status,
            statusText: response.statusText,
            message: `Laden mislukt`,
        },
    };

    const contentType = response.headers.get("Content-Type");

    if (contentType && contentType.includes("application/json")) return {
        data: await response.json(),
        error: null,
    };


    if (contentType && contentType.includes("text/html")) return {
        data: await response.text(),
        error: null,
    };

    return {
        data: null,
        error: null,
    };
}

/**
 * Creates an API handler for making HTTP requests to a specified URL.
 * 
 * @param {string} url - The base URL for the API endpoint
 * 
 * @example
 * const api = useApiHandler('https://api.example.com/user');
 * const data = await api.Get({ extends: '/1' });
 * await api.Post({ body: { name: 'John' } });
 */
export const useApiHandler = (url) => {

    /**
     * Sends an HTTP request to the API endpoint with optional configuration.
     *
     * @async
     * @param {ApiOptions} options - Configuration options for the fetch request
     * @returns {Promise<ApiResponse>} ApiResponse object containing data and error
     * @description Constructs the full API URL by optionally extending the base URL,
     * stringifies the body if provided, and executes the fetch request with error handling
     */
    const Send = async (options) => {
        const extendedUrl = options?.extends ? `${url}${options.extends}` : url;
        return await catcher(fetch(extendedUrl, {
            ...options, body: options.body ? JSON.stringify(options.body) : null
        }))
    }

    /**
     * Sends a GET request to the API endpoint.
     *
     * @async
     * @param {ApiOptions} options - Configuration options for the GET request
     * @returns {Promise<ApiGetResponse>} An object containing data, error, and refresh function
     */
    const Get = async (options) => {

        const refresh = async () => await Send({
            ...options, method: 'GET'
        });

        const response = await Send({
            ...options, method: 'GET'
        });

        return { ...response, refresh };
    }

    /**
     * Sends a POST request to the API endpoint with JSON content-type.
     *
     * @async
     * @param {ApiOptions} options - Configuration options for the POST request
     * @returns {Promise<ApiResponse>} ApiResponse object containing data and error
     */
    const Post = async (options) => Send({
        ...options, method: 'POST', headers: {
            'Content-Type': 'application/json',
        }
    })

    /**
     * Sends a PATCH request to the API endpoint with JSON content-type.
     *
     * @async
     * @param {ApiOptions} options - Configuration options for the PATCH request
     * @returns {Promise<ApiResponse>} ApiResponse object containing data and error
     */
    const Patch = async (options) => Send({
        ...options, method: 'PATCH', headers: {
            'Content-Type': 'application/json',
        }
    })

    /**
     * Sends a DELETE request to the API endpoint with JSON content-type.
     *
     * @async
     * @param {ApiOptions} options - Configuration options for the DELETE request
     * @returns {Promise<ApiResponse>} ApiResponse object containing data and error
     */
    const Delete = async (options) => Send({
        ...options, method: 'DELETE', headers: {
            'Content-Type': 'application/json',
        }
    })

    return {
        Send, Get, Post, Delete, Patch
    }

}

