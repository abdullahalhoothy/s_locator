import React, { Component } from 'react';
import styles from './UserProfile.module.css';

interface UserProfileState {
  name: string;
  email: string;
  phone: string;
  address: string;
  creditCard: string;
  showProfile: boolean;
}

class UserProfile extends Component<{}, UserProfileState> {
  constructor(props: {}) {
    super(props);
    this.state = {
      name: '',
      email: '',
      phone: '',
      address: '',
      creditCard: '',
      showProfile: false
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.toggleProfile = this.toggleProfile.bind(this);
  }

  handleChange(event: React.ChangeEvent<HTMLInputElement>): void {
    const { name, value } = event.target;
    // Only allow numeric input for phone and credit card fields
    if ((name === 'phone' || name === 'creditCard') && !/^\d*$/.test(value)) {
      return;
    }
    this.setState({ [name]: value } as unknown as Pick<UserProfileState, keyof UserProfileState>);
  }

  handleSubmit(event: React.FormEvent): void {
    event.preventDefault();
    // Perform your form submission logic here
    console.log('User Info Submitted:', this.state);
    this.toggleProfile();
  }

  toggleProfile(): void {
    this.setState({ showProfile: !this.state.showProfile });
  }

  render() {
    return (
      <div className={styles['profile-container']}>
        <button onClick={this.toggleProfile} className={styles['profile-toggle']}>
          {this.state.showProfile ? 'Hide Profile' : 'Edit Profile'}
        </button>
        {this.state.showProfile && (
          <form onSubmit={this.handleSubmit} className={styles['profile-form']}>
            <h2>User Profile</h2>
            <div className={styles['form-group']}>
              <label htmlFor="name">Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={this.state.name}
                onChange={this.handleChange}
                required
              />
            </div>
            <div className={styles['form-group']}>
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={this.state.email}
                onChange={this.handleChange}
                required
              />
            </div>
            <div className={styles['form-group']}>
              <label htmlFor="phone">Phone</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={this.state.phone}
                onChange={this.handleChange}
                required
                pattern="\d*"
              />
            </div>
            <div className={styles['form-group']}>
              <label htmlFor="address">Address</label>
              <input
                type="text"
                id="address"
                name="address"
                value={this.state.address}
                onChange={this.handleChange}
                required
              />
            </div>
            <div className={styles['form-group']}>
              <label htmlFor="creditCard">Credit Card</label>
              <input
                type="text"
                id="creditCard"
                name="creditCard"
                value={this.state.creditCard}
                onChange={this.handleChange}
                required
                pattern="\d*"
              />
            </div>
            <button type="submit" className={styles['btn-primary']}>Save</button>
          </form>
        )}
      </div>
    );
  }
}

export default UserProfile;
