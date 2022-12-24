import axios from "axios";
import jwtDecode from "jwt-decode";
import { BASE_URL } from "config/Constants";

class CustomAxios {
  static _instance = new CustomAxios();
  static instance = () => {
    return CustomAxios._instance;
  };

  constructor() {
    this.publicAxios = axios.create({ baseURL: BASE_URL });
    this.privateAxios = axios.create({
      baseURL: BASE_URL,
      withCredentials: true,
    });
    this.privateAxios.interceptors.request.use(this._requestPrivateInterceptor);
  }

  _requestPrivateInterceptor = async (config) => {
    // access_token이 정상일 경우 -> 토큰 전송
    // access_token이 비정상일 경우 -> refresh_token이 정상 / 비정상
    // refresh_token이 비정상이면 로그아웃 처리
    // refresh_token이 정상이면 통신해서 access_token 재발급 후 토큰 전송

    const accessToken = localStorage.getItem("accessToken");
    const refreshToken = localStorage.getItem("refreshToken");

    // 토큰이 없을 경우
    if (accessToken == null || refreshToken == null) {
      throw new axios.Cancel("토큰이 없습니다.");
    }

    // accessToken 확인
    if (accessToken == null || jwtDecode(accessToken).exp < Date.now() / 1000) {
      // accessToken 무효
      // refreshToken 확인
      if (
        refreshToken == null ||
        jwtDecode(refreshToken).exp < Date.now() / 1000
      ) {
        // refreshToken 무효
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        // throw 를 해도 되고
        alert("모든 토큰이 만료되었습니다.");
        window.location.replace("/login");
      } else {
        // refreshToken 유효
        const response = await customAxios.publicAxios({
          method: `post`,
          url: `/api/v1/sign/refresh`,
          data: { refreshToken },
        });

        if (response.status !== 200) {
          // window.location.replace("/login"); 를 해도 되고
          throw new axios.Cancel("리프레시 토큰이 만료되었습니다.");
        } else {
          // 토큰 재발급
          const tokens = response.data.content;
          localStorage.setItem("accessToken", tokens.accessToken);
          localStorage.setItem("refreshToken", tokens.refreshToken);
          config.headers["Authorization"] = `Bearer ${tokens.accessToken}`;
        }
      }
    } else {
      // accessToken 유효
      config.headers["Authorization"] = `Bearer ${accessToken}`;
    }

    return config;
  };
}

export const customAxios = CustomAxios.instance();
