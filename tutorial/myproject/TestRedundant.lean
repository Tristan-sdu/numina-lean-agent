import Mathlib

example (a b : Nat) : a + b = b + a := by
  have unused_have : a = a := by rfl
  rw [Nat.add_comm]