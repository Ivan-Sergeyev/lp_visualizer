import { useEffect, useState } from 'react';

interface NumberInputProps {
  value: number;
  onChange: (v: number) => void;
  placeholder?: string;
  className?: string;
  step?: number;
}

/**
 * A number input that keeps a local string state while the user is typing,
 * and only propagates a parsed number to the parent on blur or Enter.
 */
export function NumberInput({ value, onChange, placeholder, className, step = 1 }: NumberInputProps) {
  const [local, setLocal] = useState(String(value));

  // Sync when parent changes the value externally.
  useEffect(() => {
    setLocal(String(value));
  }, [value]);

  function commit(raw: string) {
    const parsed = parseFloat(raw);
    if (!isNaN(parsed)) onChange(parsed);
    else setLocal(String(value)); // revert to last valid
  }

  return (
    <input
      type="number"
      className={className}
      value={local}
      placeholder={placeholder}
      step={step}
      onChange={e => setLocal(e.target.value)}
      onBlur={e => commit(e.target.value)}
      onKeyDown={e => { if (e.key === 'Enter') commit((e.target as HTMLInputElement).value); }}
    />
  );
}
