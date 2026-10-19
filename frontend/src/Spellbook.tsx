
import { useEffect, useState } from 'react'
import { getSpellSchools, getSpells } from './api/client'
import type { Spell } from './api/client'
import './Spellbook.css'

const spellLevels = [
  { value: '', label: 'All levels' },
  { value: '0', label: 'Cantrips' },
  { value: '1', label: 'Level 1' },
  { value: '2', label: 'Level 2' },
  { value: '3', label: 'Level 3' },
  { value: '4', label: 'Level 4' },
  { value: '5', label: 'Level 5' },
  { value: '6', label: 'Level 6' },
  { value: '7', label: 'Level 7' },
  { value: '8', label: 'Level 8' },
  { value: '9', label: 'Level 9' },
]

function getLevelLabel(level: number) {
  return level === 0 ? 'Cantrip' : `Level ${level}`
}

export default function Spellbook() {
  const [spells, setSpells] = useState<Spell[]>([])
  const [schools, setSchools] = useState<string[]>([])
  const [search, setSearch] = useState('')
  const [level, setLevel] = useState('')
  const [school, setSchool] = useState('')
  const [selectedSpell, setSelectedSpell] = useState<Spell | null>(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const pageSize = 50
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getSpellSchools()
      .then(setSchools)
      .catch(() => setSchools([]))
  }, [])

  useEffect(() => {
    let cancelled = false

    async function loadSpells() {
      setLoading(true)
      setError('')

      try {
        const result = await getSpells({
          search,
          level: level === '' ? undefined : Number(level),
          school: school || undefined,
          limit: pageSize,
          offset: page * pageSize,
        })

        if (!cancelled) {
          setSpells(result.items)
          setTotal(result.total)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Could not load spells.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadSpells()

    return () => {
      cancelled = true
    }
  }, [search, level, school, page])

  return (
    <section className="spellbook">
      <header className="spellbook-header">
        <div>
          <p className="spellbook-eyebrow">ARCANE KNOWLEDGE</p>
          <h1>Spellbook</h1>
          <p className="spellbook-subtitle">
            Explore spells, discover their secrets, and prepare for your next adventure.
          </p>
        </div>

        <div className="spellbook-count">
          <span>✧</span>
          <strong>{total}</strong>
          <small>spells discovered</small>
        </div>
      </header>

      <div className="spellbook-filters">
        <label className="spellbook-search">
          <span>⌕</span>
          <input
            type="search"
            placeholder="Search spells..."
            value={search}
            onChange={(event) => {
              setSearch(event.target.value)
              setPage(0)
            }}
          />
        </label>

        <select
          aria-label="Filter by level"
          value={level}
          onChange={(event) => {
            setLevel(event.target.value)
            setPage(0)
          }}
        >
          {spellLevels.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>

        <select
          aria-label="Filter by school"
          value={school}
          onChange={(event) => {
            setSchool(event.target.value)
            setPage(0)
          }}
        >
          <option value="">All schools</option>
          {schools.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="spellbook-error">{error}</p>}

      {loading ? (
        <div className="spellbook-message">
          Consulting the ancient tomes...
        </div>
      ) : spells.length === 0 ? (
        <div className="spellbook-empty">
          <span>✧</span>
          <h2>No spells found</h2>
          <p>Try changing your search or filters.</p>
        </div>
      ) : (
        <>
          <div className="spellbook-grid">
            {spells.map((spell) => (
              <button
                type="button"
                className="spell-card"
                key={spell.id}
                onClick={() => setSelectedSpell(spell)}
              >
                <div className="spell-card-top">
                  <span className="spell-card-icon">✧</span>
                  <span className="spell-level">
                    {getLevelLabel(spell.level)}
                  </span>
                </div>

                <h2>{spell.name}</h2>
                <p className="spell-school">{spell.school}</p>
                <p className="spell-description">{spell.description}</p>
                <span className="spell-card-link">
                  View spell details ↗
                </span>
              </button>
            ))}
          </div>

          <div className="spellbook-pagination">
            <p className="spellbook-pagination-note">
              {`Showing ${page * pageSize + 1}–${page * pageSize + spells.length} of ${total} spells`}
            </p>

            <div className="spellbook-pagination-controls">
              <button
                type="button"
                className="spellbook-page-button"
                disabled={page === 0 || loading}
                onClick={() => setPage((current) => current - 1)}
              >
                ← Previous
              </button>

              <span className="spellbook-page-number">
                Page {page + 1} of {Math.max(1, Math.ceil(total / pageSize))}
              </span>

              <button
                type="button"
                className="spellbook-page-button"
                disabled={(page + 1) * pageSize >= total || loading}
                onClick={() => setPage((current) => current + 1)}
              >
                Next →
              </button>
            </div>
          </div>
        </>
      )}

      {selectedSpell && (
        <div
          className="spell-modal-backdrop"
          onClick={() => setSelectedSpell(null)}
        >
          <section
            className="spell-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="spell-modal-title"
            onClick={(event) => event.stopPropagation()}
          >
            <button
              type="button"
              className="spell-modal-close"
              aria-label="Close spell details"
              onClick={() => setSelectedSpell(null)}
            >
              ×
            </button>

            <p className="spellbook-eyebrow">{selectedSpell.school}</p>
            <h2 id="spell-modal-title">{selectedSpell.name}</h2>
            <span className="spell-level">
              {getLevelLabel(selectedSpell.level)}
            </span>

            <div className="spell-detail-stats">
              <div>
                <span>Casting time</span>
                <strong>{selectedSpell.casting_time}</strong>
              </div>
              <div>
                <span>Range</span>
                <strong>{selectedSpell.spell_range}</strong>
              </div>
              <div>
                <span>Duration</span>
                <strong>{selectedSpell.duration}</strong>
              </div>
            </div>

            <div className="spell-detail-description">
              <h3>Description</h3>
              <p>{selectedSpell.description}</p>
            </div>
          </section>
        </div>
      )}
    </section>
  )
}
