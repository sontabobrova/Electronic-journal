import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "sm" | "md";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  icon?: ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
};

export function Button({ children, className = "", icon, size = "md", type = "button", variant = "secondary", ...props }: ButtonProps) {
  return (
    <button className={`ui-button ui-button--${variant} ui-button--${size} ${className}`.trim()} type={type} {...props}>
      {icon ? <span className="ui-button__icon">{icon}</span> : null}
      {children ? <span>{children}</span> : null}
    </button>
  );
}
