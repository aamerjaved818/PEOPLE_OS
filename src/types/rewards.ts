export interface Reward {
  id: number;
  title: string;
  description: string;
  pointsRequired: number;
  category: string;
  imageUrl?: string;
  isActive: boolean;
}

export interface Recognition {
  id: number;
  senderId: string;
  receiverId: string;
  message: string;
  category: string;
  pointsAwarded: number;
  createdAt: string;
}

export interface RewardPoint {
  id: number;
  employeeId: string;
  balance: number;
  totalEarned: number;
  totalRedeemed: number;
}

export interface RewardPointTransaction {
  id: number;
  employeeId: string;
  points: number;
  type: 'EARNED' | 'REDEEMED' | 'ADJUSTED';
  description?: string;
  referenceId?: string;
  createdAt: string;
}
