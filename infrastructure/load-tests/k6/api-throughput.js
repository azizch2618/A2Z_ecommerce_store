import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  scenarios: {
    constant_throughput: {
      executor: "constant-arrival-rate",
      rate: 100,
      timeUnit: "1s",
      duration: "2m",
      preAllocatedVUs: 20,
      maxVUs: 100,
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<1500"],
  },
};

const API = __ENV.API_URL || "http://localhost:8000";

export default function apiThroughput() {
  const endpoints = [
    "/api/v1/health/",
    "/api/v1/ready/",
    "/api/v1/catalog/products/?page_size=12",
  ];

  for (const path of endpoints) {
    const res = http.get(`${API}${path}`);
    check(res, { [`${path} ok`]: (r) => r.status >= 200 && r.status < 500 });
  }

  sleep(0.1);
}
