import type { AxiosRequestConfig } from "axios";

declare module "axios" {
  export interface AxiosRequestConfig {
    /** Skip attaching guest `X-Session-Key` header */
    skipSessionKey?: boolean;
  }
}

export {};
