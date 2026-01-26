import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingProps {
  message?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const Loading: React.FC<LoadingProps> = ({
  message = 'Loading...',
  className = '',
  size = 'md',
}) => {
  const sizeMap = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`flex flex-col items-center justify-center p-4 ${className}`}>
      <Loader2 className={`${sizeMap[size]} animate-spin text-primary mb-2`} />
      {message && (
        <p className="text-xs font-bold text-text-muted uppercase tracking-wider animate-pulse">
          {message}
        </p>
      )}
    </div>
  );
};

export default Loading;
