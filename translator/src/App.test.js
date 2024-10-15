import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App Component', () => {
  test('renders the title correctly', () => {
    render(<App />);
    const titleElement = screen.getByText(/Select a Page to Monitor/i);
    expect(titleElement).toBeInTheDocument();
  });

  test('renders the Start Capture button', () => {
    render(<App />);
    const buttonElement = screen.getByText(/Start Capture/i);
    expect(buttonElement).toBeInTheDocument();
  });

  test('renders identified text message', () => {
    render(<App />);
    const messageElement = screen.getByText(/No text identified yet/i);
    expect(messageElement).toBeInTheDocument();
  });
});
