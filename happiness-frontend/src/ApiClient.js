import axios from "axios";
import { Keys } from "./keys";


const BASE_API_URL = process.env.REACT_APP_BASE_API_URL;

export default class ApiClient {
  async request(options) {
    console.log(process.env)
    console.log(`options url: ${options.url}`)
    console.log(`base api url: ${BASE_API_URL}`)
    return axios({
      method: options.method,
      url: BASE_API_URL + "/api" + options.url,
      params: new URLSearchParams(options.query),
      headers: {
        Authorization: "Bearer " + localStorage.getItem(Keys.TOKEN),
        ...options.headers,
      },
      data: options.body,
    });
  }

  async get(url, query, options) {
    return this.request({ method: "get", url, query, ...options });
  }

  async post(url, body, options) {
    return this.request({ method: "post", url, body, ...options });
  }

  async put(url, body, options) {
    return this.request({ method: "put", url, body, ...options });
  }

  async delete(url, options) {
    return this.request({ method: "delete", url, ...options });
  }
}
