import { useEffect, useState } from 'react';

interface NumberInputProps {
  value:        number;
  onChange:     (v: number) => void;
  placeholder?: string;
  className?:   string;
  step?:        number;
  'aria-label'?: string;
}

/**
 * Parses a raw input string to a number, returning NaN for empty strings or
 * strings with non-numeric content (e.g. "3abc"). Uses Number() rather than
 * parseFloat() so that trailing garbage is rejected rather than silently ignored.
 */
function parseInputValue(raw: string): number {
  return raw.trim() === '' ? NaN : Number(raw);
}

/**
 * A number `<input>` with deferred commit semantics.
 *
 * Keeps a local string state while the user is typing so partial values (e.g. a
 * lone `-`) don't trigger a parse. The parent is notified only on blur or Enter.
 * If the committed string cannot be parsed as a number, the input reverts to the
 * last valid value received from the parent.
 */
export function NumberInput({ value, onChange, placeholder, className, step = 1, 'aria-label': ariaLabel }: NumberInputProps) {
  const [local, setLocal] = useState(String(value));

  // Keep local state in sync when the parent changes value externally (e.g. a
  // reset or an undo operation that bypasses this input's own onChange path).
  useEffect(() => {
    setLocal(String(value));
  }, [value]);

  function commit(raw: string) {
    const parsed = parseInputValue(raw);
    if (!isNaN(parsed)) onChange(parsed);
    else setLocal(String(value)); // revert to last valid value
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const raw = e.target.value;
    setLocal(raw);
    // Commit immediately when the value is valid so spinner arrow clicks propagate
    // to the parent right away (they fire onChange but not onBlur).
    // Partial strings like '-' return NaN from parseInputValue and stay local only,
    // preserving the deferred-commit behaviour for keyboard entry.
    const parsed = parseInputValue(raw);
    if (!isNaN(parsed)) onChange(parsed);
  }

  return (
    <input
      type="number"
      className={className}
      value={local}
      placeholder={placeholder}
      step={step}
      aria-label={ariaLabel}
      onChange={handleChange}
      onBlur={e => commit(e.target.value)}
      onKeyDown={e => { if (e.key === 'Enter') commit((e.target as HTMLInputElement).value); }}
    />
  );
}
