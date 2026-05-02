import { useEffect, useState } from 'react';

interface NumberInputProps {
  value:        number;
  onChange:     (v: number) => void;
  placeholder?: string;
  className?:   string;
  step?:        number;
}

/**
 * A number `<input>` with deferred commit semantics.
 *
 * Keeps a local string state while the user is typing so partial values (e.g. a
 * lone `-`) don't trigger a parse. The parent is notified only on blur or Enter.
 * If the committed string cannot be parsed as a number, the input reverts to the
 * last valid value received from the parent.
 */
export function NumberInput({ value, onChange, placeholder, className, step = 1 }: NumberInputProps) {
  const [local, setLocal] = useState(String(value));

  // Keep local state in sync when the parent changes value externally (e.g. a
  // reset or an undo operation that bypasses this input's own onChange path).
  useEffect(() => {
    setLocal(String(value));
  }, [value]);

  function commit(raw: string) {
    const parsed = parseFloat(raw);
    if (!isNaN(parsed)) onChange(parsed);
    else setLocal(String(value)); // revert to last valid value
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const raw = e.target.value;
    setLocal(raw);
    // Commit immediately when the value is valid. This makes spinner arrow clicks
    // propagate to the parent right away (they fire onChange but not onBlur).
    // Partial strings like '−' fail parseFloat and are left in local state only,
    // preserving the deferred-commit behaviour for keyboard entry.
    const parsed = parseFloat(raw);
    if (!isNaN(parsed)) onChange(parsed);
  }

  return (
    <input
      type="number"
      className={className}
      value={local}
      placeholder={placeholder}
      step={step}
      onChange={handleChange}
      onBlur={e => commit(e.target.value)}
      onKeyDown={e => { if (e.key === 'Enter') commit((e.target as HTMLInputElement).value); }}
    />
  );
}
