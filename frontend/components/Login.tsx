import React, { useState } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const API_BASE_URL = 'http://localhost:5000';

interface LoginProps {
  onLogin: (token: string) => void;
}

export function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/login`, { username, password });
      const token = response.data.access_token;
      onLogin(token);
    } catch (error) {
      console.error('Login error:', error);
      setError('Invalid username or password');
    }
  };

  const handleAutoLogin = async () => {
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/login`, { 
        username: 'default_user', 
        password: 'password123' 
      });
      const token = response.data.access_token;
      onLogin(token);
    } catch (error) {
      console.error('Auto login error:', error);
      setError('Failed to auto login. Please try again.');
    }
  };

  return (
    <Card className="w-[350px] mx-auto mt-20">
      <CardHeader>
        <CardTitle>Login</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleLogin}>
          <div className="space-y-4">
            <Input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button type="submit" className="w-full">
              Login
            </Button>
            <Button type="button" onClick={handleAutoLogin} className="w-full">
              Auto Login
            </Button>
          </div>
        </form>
        {error && <p className="text-red-500 mt-2">{error}</p>}
      </CardContent>
    </Card>
  );
}