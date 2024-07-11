import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './Register.module.css';

function Register() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [companySize, setCompanySize] = useState('');
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const navigate = useNavigate();

  function handleFirstNameChange(e: React.ChangeEvent<HTMLInputElement>) {
    setFirstName(e.target.value);
  }

  function handleLastNameChange(e: React.ChangeEvent<HTMLInputElement>) {
    setLastName(e.target.value);
  }

  function handleEmailChange(e: React.ChangeEvent<HTMLInputElement>) {
    setEmail(e.target.value);
  }

  function handlePasswordChange(e: React.ChangeEvent<HTMLInputElement>) {
    setPassword(e.target.value);
  }

  function handleCompanySizeChange(e: React.ChangeEvent<HTMLSelectElement>) {
    setCompanySize(e.target.value);
  }

  function handleAcceptedTermsChange(e: React.ChangeEvent<HTMLInputElement>) {
    setAcceptedTerms(e.target.checked);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    // Perform registration logic here
    // navigate('/dashboard');
  }

  return (
    <div className={styles.registerContainer}>
      <form onSubmit={handleSubmit} className={styles.registerForm}>
        <h2>Sign up</h2>
        <div className={styles.formGroup}>
          <label htmlFor="firstName">First name*</label>
          <input
            type="text"
            id="firstName"
            value={firstName}
            onChange={handleFirstNameChange}
            required
          />
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="lastName">Last name*</label>
          <input
            type="text"
            id="lastName"
            value={lastName}
            onChange={handleLastNameChange}
            required
          />
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="email">Work email*</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={handleEmailChange}
            required
          />
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="companySize">Company size*</label>
          <select
            id="companySize"
            value={companySize}
            onChange={handleCompanySizeChange}
            required
          >
            <option value="">Please Select</option>
            <option value="small">1-10 employees</option>
            <option value="medium">11-50 employees</option>
            <option value="large">51-200 employees</option>
            <option value="xlarge">200+ employees</option>
          </select>
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="password">Password*</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={handlePasswordChange}
            required
          />
        </div>
        <div className={styles.formGroup}>
          <input
            type="checkbox"
            id="acceptedTerms"
            checked={acceptedTerms}
            onChange={handleAcceptedTermsChange}
            required
          />
          <label htmlFor="acceptedTerms">
            I accept the <Link to="/license">License Agreement</Link> and <Link to="/privacy">Privacy Policy</Link>*
          </label>
        </div>
        <button type="submit" className={styles.btnPrimary}>Create Account</button>
        <p>
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  );
}

export default Register;
