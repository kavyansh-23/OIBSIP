# 🔒 Cryptographically Secure Password Generator

A feature-rich GUI application built with Python using `tkinter`, `secrets` (for cryptographic security), and `pyperclip` for seamless clipboard management.

---

## ✨ Features

- **Cryptographic Security**: Powered by Python's native `secrets` library (CS-PRNG).
- **Security Rule Enforcement**: Guarantees at least one character from each selected category.
- **Dynamic Strength Indicator**: Live visual bar evaluating length and character diversity (Weak / Medium / Strong).
- **Customizable Criteria**:
  - Length selection (Slider & Spinbox from 8 to 128 characters).
  - Uppercase, Lowercase, Digits, and Symbols checkboxes (Minimum 2 required).
  - Option to filter out ambiguous characters (`0, O, 1, l, I`).
- **Clipboard Integration**: Instant "Copy to Clipboard" button and optional auto-copy upon generation.
- **In-Memory Session History**: Displays the last 5 generated passwords (kept strictly in RAM for privacy).

---

## 🛠️ Tech Stack

- **GUI Framework**: `tkinter`, `ttk`
- **Randomization Engine**: `secrets`, `string`
- **Clipboard Management**: `pyperclip`

---

## 🚀 How to Run

1. Navigate to the project directory:
   ```bash
   cd Python-Task3-PasswordGeneratorcd ~/OIBSIP
mkdir -p Python-Task3-PasswordGenerator/proofs
cd Python-Task3-PasswordGenerator

# 1. Create requirements.txt
cat << 'EOF' > requirements.txt
pyperclip
