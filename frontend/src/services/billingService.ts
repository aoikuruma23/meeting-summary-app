import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://meeting-summary-app-backend.jibunkaikaku-lab.com';

// 認証トークンを取得する関数
const getAuthToken = (): string | null => {
  return localStorage.getItem('access_token');
};

// APIクライアントの設定
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプターでトークンを自動追加
apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface CheckoutSessionResponse {
  success: boolean;
  message: string;
  data: {
    url: string;
  };
}

export interface PortalSessionResponse {
  success: boolean;
  message: string;
  data: {
    url: string;
  };
}

export interface SubscriptionStatusResponse {
  success: boolean;
  message: string;
  data: {
    isActive: boolean;
    plan: string;
    currentPeriodEnd: string;
    cancelAtPeriodEnd: boolean;
  };
}

export interface PricingInfoResponse {
  success: boolean;
  message: string;
  data: {
    monthlyPrice: number;
    freeTrialDays: number;
    freeUsageLimit: number;
  };
}

export const billingService = {
  /**
   * チェックアウトセッションを作成
   */
  async createCheckoutSession(planId: string): Promise<CheckoutSessionResponse> {
    try {
      const response = await apiClient.post('/api/billing/checkout', {
        plan_id: planId,
      });
      return response.data;
    } catch (error) {
      console.error('チェックアウトセッション作成エラー:', error);
      throw error;
    }
  },

  /**
   * ポータルセッションを作成（サブスクリプション管理）
   */
  async createPortalSession(): Promise<PortalSessionResponse> {
    try {
      const response = await apiClient.post('/api/billing/portal');
      return response.data;
    } catch (error) {
      console.error('ポータルセッション作成エラー:', error);
      throw error;
    }
  },

  /**
   * サブスクリプション状態を取得
   */
  async getSubscriptionStatus(): Promise<SubscriptionStatusResponse> {
    try {
      const response = await apiClient.get('/api/billing/subscription');
      return response.data;
    } catch (error) {
      console.error('サブスクリプション状態取得エラー:', error);
      throw error;
    }
  },

  /**
   * 価格情報を取得
   */
  async getPricingInfo(): Promise<PricingInfoResponse> {
    try {
      const response = await apiClient.get('/api/billing/pricing');
      return response.data;
    } catch (error) {
      console.error('価格情報取得エラー:', error);
      throw error;
    }
  },

  /**
   * アクセス権限をチェック
   */
  async checkAccess(): Promise<{ success: boolean; message: string; data: { hasAccess: boolean } }> {
    try {
      const response = await apiClient.get('/api/billing/access');
      return response.data;
    } catch (error) {
      console.error('アクセス権限チェックエラー:', error);
      throw error;
    }
  },
}; 