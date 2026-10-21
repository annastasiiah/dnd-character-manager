
import { useEffect, useState } from 'react'
import {
  getRaces,
  getClasses,
  getBackgrounds,
} from './api/client'
import './Compendium.css'

type Entry = {
  id: number
  name: string
  description?: string | null
  speed?: number | null
}

type Category = 'races' | 'classes' | 'backgrounds'

const categories: { id: Category; label: string }[] = [
  { id: 'races', label: 'Races' },
  { id: 'classes', label: 'Classes' },
  { id: 'backgrounds', label: 'Backgrounds' },
]

export default function Compendium() {
  const [category, setCategory] = useState<Category>('races')
  const [races, setRaces] = useState<Entry[]>([])
  const [classes, setClasses] = useState<Entry[]>([])
  const [backgrounds, setBackgrounds] = useState<Entry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadCompendium() {
      setLoading(true)
      setError('')

      try {
        const [raceData, classData, backgroundData] = await Promise.all([
          getRaces(),
          getClasses(),
          getBackgrounds(),
        ])

        if (cancelled) return

        setRaces(raceData)
        setClasses(classData)
        setBackgrounds(backgroundData)
      } catch {
        if (!cancelled) {
          setError('Could not load the compendium. Please try again.')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    loadCompendium()

    return () => {
      cancelled = true
    }
  }, [])

  const entries =
    category === 'races'
      ? races
      : category === 'classes'
        ? classes
        : backgrounds

  const filteredEntries = entries.filter((entry) =>
    entry.name.toLowerCase().includes(search.trim().toLowerCase()),
  )

  return (
    <div className="compendium">
      <header className="compendium-header">
        <p className="compendium-eyebrow">THE WORLD OF ADVENTURE</p>
        <h1>Compendium</h1>
        <p className="compendium-subtitle">
          Explore the origins, paths, and stories of your next character.
        </p>
      </header>

      <nav className="compendium-tabs" aria-label="Compendium categories">
        {categories.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`compendium-tab ${
              category === item.id ? 'active' : ''
            }`}
            onClick={() => setCategory(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>
      <div className="compendium-search">
        <span aria-hidden="true">⌕</span>
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search the compendium..."
          aria-label="Search compendium"
        />
        {search && (
          <button type="button" onClick={() => setSearch('')} aria-label="Clear search">
            ×
          </button>
        )}
      </div>

      {loading ? (
        <p className="compendium-message">Opening the archives...</p>
      ) : error ? (
        <div className="compendium-message compendium-error">
          <p>{error}</p>
          <button type="button" onClick={() => window.location.reload()}>
            Try again
          </button>
        </div>
      ) : filteredEntries.length === 0 ? (
          <p className="compendium-message">
            {search
              ? 'No entries match your search.'
              : 'No entries found in this section yet.'}
          </p>
        ) : (
        <>
          <div className="compendium-section-heading">
            <h2>{categories.find((item) => item.id === category)?.label}</h2>
            <span>{filteredEntries.length} entries</span>
          </div>

          <div className="compendium-grid">
            {filteredEntries.map((entry) => (
              <article className="compendium-card" key={entry.id}>
                <div className="compendium-card-mark">✦</div>
                <h3>{entry.name}</h3>

                {category === 'races' && entry.description && (
                  <p className="compendium-description">
                    {entry.description}
                  </p>
                )}

                {category === 'races' && entry.speed != null && (
                  <div className="compendium-stat">
                    <span>Speed</span>
                    <strong>{entry.speed} ft.</strong>
                  </div>
                )}

                {category !== 'races' && (
                  <p className="compendium-description">
                    {category === 'classes'
                      ? 'A path to shape your adventurer.'
                      : 'A story that shaped your character.'}
                  </p>
                )}
              </article>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
