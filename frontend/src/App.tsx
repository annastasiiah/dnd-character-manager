import { useEffect, useState } from 'react'
import Spellbook from './Spellbook'
import CreateCharacterForm from './CreateCharacterForm.tsx'
import Compendium from './Compendium'
import AuthForm from './AuthForm'
import {
  getCharacters,
  getMe,
  updateCharacter,
  deleteCharacter,
  type Character,
  type User,
} from './api/client'
import './App.css'

function App() {
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem('access_token'),
  )
  const [user, setUser] = useState<User | null>(null)
  const [characters, setCharacters] = useState<Character[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [activePage, setActivePage] = useState<
      'characters' | 'spellbook' | 'compendium'
    >('characters')
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null)
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null)

  useEffect(() => {
    if (!token) {
      setUser(null)
      setCharacters([])
      setLoading(false)
      return
    }

    const accessToken = token
    let cancelled = false

    async function loadData() {
      setLoading(true)
      setError('')

      try {
        const [profile, party] = await Promise.all([
          getMe(accessToken),
          getCharacters(accessToken),
        ])

        if (!cancelled) {
          setUser(profile)
          setCharacters(party)
        }
      } catch (err) {
        if (!cancelled) {
          localStorage.removeItem('access_token')
          setToken(null)
          setUser(null)
          setCharacters([])
          setError(
            err instanceof Error
              ? err.message
              : 'Не вдалося завантажити дані.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadData()

    return () => {
      cancelled = true
    }
  }, [token])

  function handleAuthenticated(newToken: string) {
    localStorage.setItem('access_token', newToken)
    setToken(newToken)
  }

  function handleLogout() {
    localStorage.removeItem('access_token')
    setToken(null)
    setUser(null)
    setCharacters([])
    setError('')
  }

  async function handleCharacterCreated() {
  if (!token) return

  try {
    const updatedCharacters = await getCharacters(token)
    setCharacters(updatedCharacters)
    setShowCreateForm(false)
    setError('')
  } catch (err) {
    setError(
      err instanceof Error
        ? err.message
        : 'Персонажа створено, але не вдалося оновити список.',
    )
  }
}

async function handleCharacterDeleted(characterId: number) {
  if (!token) return

  const confirmed = window.confirm(
    'Ви впевнені, що хочете видалити цього персонажа? Цю дію не можна скасувати.',
  )

  if (!confirmed) return

  try {
    await deleteCharacter(token, characterId)

    setCharacters((current) =>
      current.filter((character) => character.id !== characterId),
    )

    setSelectedCharacter(null)
    setEditingCharacter(null)
    setError('')
  } catch (err) {
    setError(
      err instanceof Error
        ? err.message
        : 'Не вдалося видалити персонажа.',
    )
  }
}

  if (!token) {
    return <AuthForm onAuthenticated={handleAuthenticated} />
  }

  if (loading) {
    return (
      <main className="auth-page">
        <p>Завантаження твого Grimoire…</p>
      </main>
    )
  }

  if (!user) {
    return (
      <main className="auth-page">
        <p role="alert">
          {error || 'Не вдалося завантажити профіль.'}
        </p>
        <button className="primary-button" onClick={handleLogout}>
          Повернутися до входу
        </button>
      </main>
    )
  }


return (
  <div className="app-shell">
    <aside className="sidebar">
      <a
        className="brand"
        href="#"
        onClick={(event) => {
          event.preventDefault()
          setActivePage('characters')
        }}
      >
        <span className="brand-mark">✦</span>
        <span>
          <strong>Grimoire</strong>
          <small>CHARACTER MANAGER</small>
        </span>
      </a>

      <div className="sidebar-label">WORKSPACE</div>

      <nav className="navigation">
        <button
          type="button"
          className={`nav-link ${activePage === 'characters' ? 'active' : ''}`}
          onClick={() => setActivePage('characters')}
        >
          <span>♙</span> My characters
        </button>

        <button
          type="button"
          className={`nav-link ${activePage === 'spellbook' ? 'active' : ''}`}
          onClick={() => setActivePage('spellbook')}
        >
          <span>✧</span> Spellbook
        </button>

        <button
          type="button"
          className={`nav-link ${activePage === 'compendium' ? 'active' : ''}`}
          onClick={() => {
            console.log('Compendium clicked')
            setActivePage('compendium')
          }}
        >
          <span>▤</span> Compendium
        </button>
      </nav>

      <div className="sidebar-bottom">
        <div className="profile-avatar">
          {user.nickname.slice(0, 1).toUpperCase()}
        </div>

        <div className="profile-info">
          <strong>{user.nickname}</strong>
          <small>
            {user.role === 'admin' ? 'Administrator' : 'Adventurer'}
          </small>
        </div>

        <button
          className="profile-menu"
          type="button"
          onClick={handleLogout}
          aria-label="Вийти з акаунта"
          title="Вийти з акаунта"
        >
          ↪
        </button>
      </div>
    </aside>

    <main className="main-content">
      <header className="topbar">
        <div className="breadcrumb">
          Workspace <span>/</span>{' '}
          {activePage === 'characters'
            ? 'My characters'
            : activePage === 'spellbook'
              ? 'Spellbook'
              : 'Compendium'}
        </div>

        <div className="topbar-right">
          <span className="status-dot" />
          <span>Adventurer's journal</span>
        </div>
      </header>

      <section className="page-content">
        {activePage === 'characters' && (
          <>
            <div className="hero">
              <div className="hero-copy">
                <div className="eyebrow">
                  <span>✦</span> YOUR ADVENTURE BEGINS HERE
                </div>

                <h1>
                  Every legend
                  <br />
                  starts <em>somewhere.</em>
                </h1>

                <p>
                  Your heroes, their stories, and the worlds they will change.
                  Keep every detail of your next great adventure in one place.
                </p>

                <button
                  className="primary-button"
                  type="button"
                  onClick={() => setShowCreateForm(true)}
                >
                  <span>＋</span> Create character
                </button>
              </div>

              <div className="hero-art" aria-hidden="true">
                <div className="orbit orbit-one" />
                <div className="orbit orbit-two" />
                <div className="hero-symbol">✧</div>
                <span className="star star-one">✦</span>
                <span className="star star-two">✧</span>
                <span className="star star-three">·</span>
                <div className="hero-caption">
                  <span>✦</span> THE ADVENTURER'S JOURNAL
                </div>
              </div>
            </div>

            <section className="characters-section">
              <div className="section-heading">
                <div>
                  <div className="eyebrow">YOUR PARTY</div>
                  <h2>Character collection</h2>
                  <p>Your heroes are waiting for their next chapter.</p>
                </div>

                <button
                  className="secondary-button"
                  type="button"
                  onClick={() => setShowCreateForm(true)}
                >
                  ＋ New character
                </button>
              </div>

              <div className="collection-toolbar">
                <span>
                  {characters.length}{' '}
                  {characters.length === 1 ? 'character' : 'characters'}
                </span>

                <button className="filter-button" type="button">
                  ☷ &nbsp; All characters
                </button>
              </div>

              {error && (
                <p className="auth-error" role="alert">
                  {error}
                </p>
              )}

              {characters.length === 0 ? (
                <div className="character-empty">
                  <span>✧</span>
                  <h3>Your story begins here</h3>
                  <p>You haven't created any characters yet.</p>
                </div>
              ) : (
                <div className="character-grid">
                  {characters.map((character) => (
                    <article className="character-card" key={character.id}>
                      <div className="character-art lavender">
                        <span className="character-rune">✧</span>
                        <span className="character-initials">
                          {character.name.slice(0, 2).toUpperCase()}
                        </span>
                        <span className="level-badge">
                          LVL {character.level}
                        </span>
                      </div>

                      <div className="character-details">
                        <div className="character-race">
                          {character.race.name}
                        </div>

                        <h3>{character.name}</h3>

                        <div className="character-class">
                          <span>✦</span> {character.character_class.name}
                        </div>

                        <div className="character-actions">
                          <button
                            className="view-character"
                            type="button"
                            onClick={() => setSelectedCharacter(character)}
                          >
                            View character <span>↗</span>
                          </button>

                          <button
                            className="edit-character"
                            type="button"
                            onClick={() => {
                              setSelectedCharacter(null)
                              setEditingCharacter(character)
                            }}
                          >
                            Edit
                          </button>

                          <button
                            className="delete-character"
                            type="button"
                            onClick={() =>
                              void handleCharacterDeleted(character.id)
                            }
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>

            <footer className="page-footer">
              <span>✦</span> MADE FOR ADVENTURERS, BY ADVENTURERS
              <span className="footer-version">GRIMOIRE · 01</span>
            </footer>
          </>
        )}

        {activePage === 'spellbook' && <Spellbook />}
        {activePage === 'compendium' && <Compendium />}

      </section>
    </main>

    {activePage === 'characters' &&
      (showCreateForm || editingCharacter) && (
        <CreateCharacterForm
          key={editingCharacter?.id ?? 'new-character'}
          token={token}
          character={editingCharacter ?? undefined}
          onCreated={async () => {
            if (!token) return

            try {
              const updatedCharacters = await getCharacters(token)
              setCharacters(updatedCharacters)
              setShowCreateForm(false)
              setEditingCharacter(null)
              setSelectedCharacter(null)
              setError('')
            } catch (err) {
              setError(
                err instanceof Error
                  ? err.message
                  : 'Не вдалося оновити список персонажів.',
              )
            }
          }}
          onCancel={() => {
            setShowCreateForm(false)
            setEditingCharacter(null)
          }}
        />
      )}

    {activePage === 'characters' && selectedCharacter && (
      <div
        className="character-modal-backdrop"
        onClick={() => setSelectedCharacter(null)}
      >
        <section
          className="character-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="character-modal-title"
          onClick={(event) => event.stopPropagation()}
        >
          <button
            className="character-modal-close"
            type="button"
            onClick={() => setSelectedCharacter(null)}
            aria-label="Close"
          >
            ×
          </button>

          <div className="eyebrow">CHARACTER SHEET</div>
          <h2 id="character-modal-title">{selectedCharacter.name}</h2>

          <p>
            {selectedCharacter.race.name} ·{' '}
            {selectedCharacter.character_class.name}
          </p>

          <p>Background: {selectedCharacter.background.name}</p>
          <p>Level: {selectedCharacter.level}</p>

          <div className="character-stats">
            {(
              [
                ['Strength', selectedCharacter.strength],
                ['Dexterity', selectedCharacter.dexterity],
                ['Constitution', selectedCharacter.constitution],
                ['Intelligence', selectedCharacter.intelligence],
                ['Wisdom', selectedCharacter.wisdom],
                ['Charisma', selectedCharacter.charisma],
              ] as const
            ).map(([label, value]) => (
              <div className="character-stat" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
                <small>
                  Modifier: {Math.floor((value - 10) / 2) >= 0 ? '+' : ''}
                  {Math.floor((value - 10) / 2)}
                </small>
              </div>
            ))}
          </div>
        </section>
      </div>
    )}
  </div>
)}

export default App