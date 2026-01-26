export interface BenefitEnrollment {
  id: string;
  name: string;
  tier: 'Standard' | 'Gold' | 'Platinum';
  date: string;
  status: 'Active' | 'Pending';
}

export interface BenefitTier {
  name: string;
  color: string;
  price: string;
  items: string[];
  icon: string;
  popular?: boolean;
}
