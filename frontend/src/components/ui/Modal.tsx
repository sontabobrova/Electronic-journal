import { X } from "lucide-react";
import type { ReactNode } from "react";
import { createPortal } from "react-dom";

import { Button } from "./Button";

type ModalProps = {
  children: ReactNode;
  footer?: ReactNode;
  isOpen: boolean;
  onClose: () => void;
  title: string;
};

export function Modal({ children, footer, isOpen, onClose, title }: ModalProps) {
  if (!isOpen) {
    return null;
  }

  return createPortal(
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="modal-panel" role="dialog" aria-modal="true" aria-label={title} onMouseDown={(event) => event.stopPropagation()}>
        <header className="modal-panel__header">
          <h2>{title}</h2>
          <Button aria-label="Закрыть" icon={<X aria-hidden="true" size={18} />} onClick={onClose} variant="ghost" />
        </header>
        <div className="modal-panel__body">{children}</div>
        {footer ? <footer className="modal-panel__footer">{footer}</footer> : null}
      </section>
    </div>,
    document.body,
  );
}
