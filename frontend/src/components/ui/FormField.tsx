import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

type BaseFieldProps = {
  error?: string;
  hint?: string;
  icon?: ReactNode;
  label: string;
};

type TextFieldProps = BaseFieldProps & InputHTMLAttributes<HTMLInputElement>;

type SelectFieldProps = BaseFieldProps &
  SelectHTMLAttributes<HTMLSelectElement> & {
    options: Array<{ label: string; value: string }>;
  };

type TextareaFieldProps = BaseFieldProps & TextareaHTMLAttributes<HTMLTextAreaElement>;

export function TextField({ error, hint, icon, label, ...props }: TextFieldProps) {
  return (
    <label className="ui-field">
      <span>{label}</span>
      <div className={`ui-field__control ${icon ? "has-icon" : ""} ${error ? "has-error" : ""}`}>
        {icon ? <span className="ui-field__icon">{icon}</span> : null}
        <input {...props} />
      </div>
      {error ? <small className="ui-field__error">{error}</small> : null}
      {!error && hint ? <small>{hint}</small> : null}
    </label>
  );
}

export function SelectField({ error, hint, icon, label, options, ...props }: SelectFieldProps) {
  return (
    <label className="ui-field">
      <span>{label}</span>
      <div className={`ui-field__control ${icon ? "has-icon" : ""} ${error ? "has-error" : ""}`}>
        {icon ? <span className="ui-field__icon">{icon}</span> : null}
        <select {...props}>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
      {error ? <small className="ui-field__error">{error}</small> : null}
      {!error && hint ? <small>{hint}</small> : null}
    </label>
  );
}

export function TextareaField({ error, hint, label, ...props }: TextareaFieldProps) {
  return (
    <label className="ui-field">
      <span>{label}</span>
      <textarea className={error ? "has-error" : ""} {...props} />
      {error ? <small className="ui-field__error">{error}</small> : null}
      {!error && hint ? <small>{hint}</small> : null}
    </label>
  );
}
