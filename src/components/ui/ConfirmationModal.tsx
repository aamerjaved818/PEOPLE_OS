import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Modal } from './Modal';
import { Button } from './Button';

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'warning' | 'info';
  isLoading?: boolean;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'danger',
  isLoading = false,
}) => {
  const getIcon = () => {
    switch (variant) {
      case 'danger':
        return <AlertTriangle className="text-red-500" size={24} />;
      case 'warning':
        return <AlertTriangle className="text-amber-500" size={24} />;
      default:
        return <AlertTriangle className="text-blue-500" size={24} />;
    }
  };

  // Button variant is determined inline via className

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="sm" showCloseButton={false} title="">
      <div className="flex flex-col items-center text-center p-4">
        <div
          className={`w-12 h-12 rounded-full flex items-center justify-center mb-4 ${
            variant === 'danger'
              ? 'bg-red-500/10'
              : variant === 'warning'
                ? 'bg-amber-500/10'
                : 'bg-blue-500/10'
          }`}
        >
          {getIcon()}
        </div>

        <h3 className="text-lg font-bold text-white mb-2 uppercase tracking-wide">{title}</h3>

        <p className="text-slate-400 text-sm mb-6 leading-relaxed">{message}</p>

        <div className="flex items-center gap-3 w-full">
          <Button
            variant="ghost"
            onClick={onClose}
            className="flex-1 text-slate-400 hover:text-white hover:bg-white/5"
            disabled={isLoading}
          >
            {cancelLabel}
          </Button>
          <Button
            // @ts-ignore - ignoring variant check to force styles if needed or rely on base
            variant={variant === 'danger' ? 'solid' : 'solid'}
            className={`flex-1 ${
              variant === 'danger'
                ? 'bg-red-600 hover:bg-red-500'
                : variant === 'warning'
                  ? 'bg-amber-600 hover:bg-amber-500'
                  : 'bg-blue-600'
            }`}
            onClick={onConfirm}
            isLoading={isLoading}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </Modal>
  );
};
