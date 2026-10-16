
import './App.css'

const characters = [
  {
    id: 1,
    name: 'Aeloria Moonwhisper',
    race: 'High Elf',
    characterClass: 'Wizard',
    level: 5,
    initials: 'AM',
    color: 'lavender',
  },
  {
    id: 2,
    name: 'Thorin Ironforge',
    race: 'Mountain Dwarf',
    characterClass: 'Fighter',
    level: 3,
    initials: 'TI',
    color: 'amber',
  },
  {
    id: 3,
    name: 'Nyx Shadowmere',
    race: 'Tiefling',
    characterClass: 'Rogue',
    level: 7,
    initials: 'NS',
    color: 'rose',
  },
]

function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#">
          <span className="brand-mark">✦</span>
          <span>
            <strong>Grimoire</strong>
            <small>CHARACTER MANAGER</small>
          </span>
        </a>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="navigation">
          <a className="nav-link active" href="#">
            <span>♙</span> My characters
          </a>
          <a className="nav-link" href="#">
            <span>✧</span> Spellbook
          </a>
          <a className="nav-link" href="#">
            <span>▤</span> Compendium
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="profile-avatar">A</div>
          <div className="profile-info">
            <strong>Adventurer</strong>
            <small>Campaign explorer</small>
          </div>
          <span className="profile-menu">···</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> My characters
          </div>
          <div className="topbar-right">
            <span className="status-dot" />
            <span>Adventurer's journal</span>
          </div>
        </header>

        <section className="page-content">
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
              <button className="primary-button" type="button">
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
              <button className="secondary-button" type="button">
                ＋ New character
              </button>
            </div>

            <div className="collection-toolbar">
              <span>{characters.length} characters</span>
              <button className="filter-button" type="button">
                ☷ &nbsp; All characters
              </button>
            </div>

            <div className="character-grid">
              {characters.map((character) => (
                <article className="character-card" key={character.id}>
                  <div className={`character-art ${character.color}`}>
                    <span className="character-rune">✧</span>
                    <span className="character-initials">
                      {character.initials}
                    </span>
                    <span className="level-badge">
                      LVL {character.level}
                    </span>
                  </div>

                  <div className="character-details">
                    <div className="character-race">{character.race}</div>
                    <h3>{character.name}</h3>
                    <div className="character-class">
                      <span>✦</span> {character.characterClass}
                    </div>
                    <button className="view-character" type="button">
                      View character <span>↗</span>
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <footer className="page-footer">
            <span>✦</span> MADE FOR ADVENTURERS, BY ADVENTURERS
            <span className="footer-version">GRIMOIRE · 01</span>
          </footer>
        </section>
      </main>
    </div>
  )
}

export default App
