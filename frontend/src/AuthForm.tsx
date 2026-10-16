
import { useState, type FormEvent } from 'react'
import { login, register } from './api/client'
import './AuthForm.css'

type AuthFormProps = {
  onAuthenticated: (token: string) => void
}

function AuthForm({ onAuthenticated }: AuthFormProps) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [nickname, setNickname] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (mode === 'register') {
        await register(email, nickname, password)
      }

      const token = await login(email, password)
      onAuthenticated(token.access_token)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Something went wrong. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  function switchMode() {
    setMode((current) => current === 'login' ? 'register' : 'login')
    setError('')
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <a className="auth-brand" href="#">
          <span className="auth-brand-mark">✦</span>
          <span>
            <strong>Grimoire</strong>
            <small>CHARACTER MANAGER</small>
          </span>
        </a>

        <div className="auth-heading">
          <div className="eyebrow">YOUR NEXT CHAPTER</div>
          <h1>
            {mode === 'login' ? (
              <>Welcome <em>back.</em></>
            ) : (
              <>Begin your <em>legend.</em></>
            )}
          </h1>
          <p>
            {mode === 'login'
              ? 'Enter your details to return to your adventures.'
              : 'Create an account to keep your heroes and stories together.'}
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            required
          />

          {mode === 'register' && (
            <>
              <label htmlFor="nickname">Nickname</label>
              <input
                id="nickname"
                type="text"
                autoComplete="nickname"
                value={nickname}
                onChange={(event) => setNickname(event.target.value)}
                placeholder="Your adventurer name"
                maxLength={50}
                required
              />
            </>
          )}

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            autoComplete={
              mode === 'login' ? 'current-password' : 'new-password'
            }
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="At least 8 characters"
            minLength={8}
            required
          />

          {error && (
            <p className="auth-error" role="alert">
              {error}
            </p>
          )}

          <button
            className="primary-button auth-submit"
            type="submit"
            disabled={loading}
          >
            {loading
              ? 'Please wait...'
              : mode === 'login'
                ? 'Enter the Grimoire'
                : 'Create your account'}
          </button>
        </form>

        <p className="auth-switch">
          {mode === 'login'
            ? "New to Grimoire?"
            : 'Already have an account?'}
          {' '}
          <button type="button" onClick={switchMode}>
            {mode === 'login' ? 'Create account' : 'Sign in'}
          </button>
        </p>

        <div className="auth-footer">
          ✦ MADE FOR ADVENTURERS, BY ADVENTURERS
        </div>
      </section>
    </main>
  )
}

export default AuthForm
