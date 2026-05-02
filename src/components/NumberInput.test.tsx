// @vitest-environment jsdom
/**
 * NumberInput — component tests
 *
 * Covers the three commit paths (onChange for valid values, blur, Enter) and the
 * two non-commit cases (partial strings that fail parseFloat, external value sync).
 *
 * The spinner-arrow regression (onChange fires but onBlur never does, so the plot
 * never updated) is covered by the "onChange with a valid number" tests: they fire
 * only onChange and assert that the parent callback is called immediately.
 */

import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { NumberInput } from './NumberInput';

// @testing-library/react needs a minimal DOM cleanup shim under jsdom.
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';
afterEach(cleanup);

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Renders a NumberInput and returns the <input> element plus the onChange spy. */
function setup(initial = 0, step = 0.5) {
  const onChange = vi.fn();
  render(<NumberInput value={initial} onChange={onChange} step={step} />);
  const input = screen.getByRole('spinbutton') as HTMLInputElement;
  return { input, onChange };
}

// ── Spinner / onChange path ───────────────────────────────────────────────────

describe('onChange (spinner arrow path)', () => {
  it('calls the parent immediately when changed to a valid number', () => {
    const { input, onChange } = setup(3);
    fireEvent.change(input, { target: { value: '3.5' } });
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith(3.5);
  });

  it('calls the parent for each successive valid change', () => {
    const { input, onChange } = setup(0);
    fireEvent.change(input, { target: { value: '1' } });
    fireEvent.change(input, { target: { value: '2' } });
    expect(onChange).toHaveBeenCalledTimes(2);
    expect(onChange).toHaveBeenLastCalledWith(2);
  });

  it('does NOT call the parent for a lone minus sign (partial value)', () => {
    const { input, onChange } = setup(0);
    fireEvent.change(input, { target: { value: '-' } });
    expect(onChange).not.toHaveBeenCalled();
  });

  it('does NOT call the parent for an empty string', () => {
    const { input, onChange } = setup(5);
    fireEvent.change(input, { target: { value: '' } });
    expect(onChange).not.toHaveBeenCalled();
  });

  it('accepts negative numbers', () => {
    const { input, onChange } = setup(0);
    fireEvent.change(input, { target: { value: '-2.5' } });
    expect(onChange).toHaveBeenCalledWith(-2.5);
  });

  it('accepts zero', () => {
    const { input, onChange } = setup(1);
    fireEvent.change(input, { target: { value: '0' } });
    expect(onChange).toHaveBeenCalledWith(0);
  });
});

// ── Blur path ─────────────────────────────────────────────────────────────────

describe('onBlur (deferred commit path)', () => {
  it('calls the parent on blur with a valid value', () => {
    const { input, onChange } = setup(0);
    fireEvent.change(input, { target: { value: '-' } }); // partial — no commit yet
    expect(onChange).not.toHaveBeenCalled();
    fireEvent.blur(input, { target: { value: '7' } });
    expect(onChange).toHaveBeenCalledWith(7);
  });

  it('reverts to the last valid value on blur when input is unparseable', async () => {
    const { input, onChange } = setup(4);
    fireEvent.change(input, { target: { value: '-' } });
    await act(async () => {
      fireEvent.blur(input, { target: { value: '-' } });
    });
    expect(onChange).not.toHaveBeenCalled();
    expect(input.value).toBe('4'); // reverted
  });
});

// ── Enter key path ────────────────────────────────────────────────────────────

describe('Enter key (deferred commit path)', () => {
  it('calls the parent on Enter with a valid value', () => {
    const { input, onChange } = setup(0);
    fireEvent.change(input, { target: { value: '9' } });
    // onChange already called via handleChange; reset the spy to isolate Enter
    onChange.mockClear();
    fireEvent.keyDown(input, { key: 'Enter', target: { value: '9' } });
    expect(onChange).toHaveBeenCalledWith(9);
  });

  it('does not call the parent on other keys', () => {
    const { input, onChange } = setup(0);
    fireEvent.change(input, { target: { value: '5' } });
    onChange.mockClear();
    fireEvent.keyDown(input, { key: 'Tab', target: { value: '5' } });
    expect(onChange).not.toHaveBeenCalled();
  });
});
