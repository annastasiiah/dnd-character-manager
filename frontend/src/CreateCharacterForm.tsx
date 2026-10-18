
import { useEffect, useState } from 'react'
import {
  createCharacter,
  getRaces,
  getClasses,
  getBackgrounds,
  type CharacterCreate,
} from './api/client'
import './CreateCharacterForm.css'

type Option = {
  id: number
  name: string
}

type Props = {
  token: string
  onCreated: () => void
  onCancel: () => void
}

const abilities = [
  { name: 'strength', label: 'Strength' },
  { name: 'dexterity', label: 'Dexterity' },
  { name: 'constitution', label: 'Constitution' },
  { name: 'intelligence', label: 'Intelligence' },
  { name: 'wisdom', label: 'Wisdom' },
  { name: 'charisma', label: 'Charisma' },
] as const

function CreateCharacterForm({ token, onCreated, onCancel }: Props) {
  const [name, setName] = useState('')
  const [raceId, setRaceId] = useState('')
  const [classId, setClassId] = useState('')
  const [backgroundId, setBackgroundId] = useState('')
  const [level, setLevel] = useState(1)

  const [stats, setStats] = useState({
    strength: 10,
    dexterity: 10,
    constitution: 10,
    intelligence: 10,
    wisdom: 10,
    charisma: 10,
  })

  const [races, setRaces] = useState<Option[]>([])
  const [classes, setClasses] = useState<Option[]>([])
  const [backgrounds, setBackgrounds] = useState<Option[]>([])
  const [loadingOptions, setLoadingOptions] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadOptions() {
      try {
        const [raceOptions, classOptions, backgroundOptions] =
          await Promise.all([
            getRaces(),
            getClasses(),
            getBackgrounds(),
          ])

        if (!cancelled) {
          setRaces(raceOptions)
          setClasses(classOptions)
          setBackgrounds(backgroundOptions)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Не вдалося завантажити довідники.',
          )
        }
      } finally {
        if (!cancelled) setLoadingOptions(false)
      }
    }

    void loadOptions()

    return () => {
      cancelled = true
    }
  }, [])

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')

    if (!raceId || !classId || !backgroundId) {
      setError('Обери расу, клас і передісторію.')
      return
    }

    const data: CharacterCreate = {
      name: name.trim(),
      race_id: Number(raceId),
      class_id: Number(classId),
      background_id: Number(backgroundId),
      level,
      ...stats,
    }

    setSaving(true)

    try {
      await createCharacter(token, data)
      onCreated()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Не вдалося створити персонажа.',
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="character-modal-backdrop">
      <section
        className="character-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-character-title"
      >
        <header className="character-modal-header">
          <div>
            <div className="eyebrow">BEGIN A NEW ADVENTURE</div>
            <h2 id="create-character-title">Create character</h2>
          </div>
          <button
            className="modal-close"
            type="button"
            onClick={onCancel}
            aria-label="Закрити форму"
          >
            ×
          </button>
        </header>

        {loadingOptions ? (
          <p>Завантажуємо раси, класи та передісторії…</p>
        ) : (
          <form onSubmit={handleSubmit}>
            <label className="form-field">
              Character name
              <input
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                maxLength={50}
                placeholder="Наприклад, Elara Moonwhisper"
                required
              />
            </label>

            <div className="form-row">
              <label className="form-field">
                Race
                <select
                  value={raceId}
                  onChange={(event) => setRaceId(event.target.value)}
                  required
                >
                  <option value="">Choose race</option>
                  {races.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </label>

              <label className="form-field">
                Class
                <select
                  value={classId}
                  onChange={(event) => setClassId(event.target.value)}
                  required
                >
                  <option value="">Choose class</option>
                  {classes.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="form-row">
              <label className="form-field">
                Background
                <select
                  value={backgroundId}
                  onChange={(event) => setBackgroundId(event.target.value)}
                  required
                >
                  <option value="">Choose background</option>
                  {backgrounds.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </label>

              <label className="form-field">
                Level
                <select
                  value={level}
                  onChange={(event) => setLevel(Number(event.target.value))}
                >
                  {Array.from({ length: 20 }, (_, i) => i + 1).map((value) => (
                    <option key={value} value={value}>
                      Level {value}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="stats-heading">
              <h3>Ability scores</h3>
              <span>Range: 1–30</span>
            </div>

            <div className="stats-grid">
              {abilities.map((ability) => (
                <label className="stat-field" key={ability.name}>
                  <span>{ability.label}</span>
                  <input
                    type="number"
                    min={1}
                    max={30}
                    required
                    value={stats[ability.name]}
                    onChange={(event) =>
                      setStats((current) => ({
                        ...current,
                        [ability.name]: Number(event.target.value),
                      }))
                    }
                  />
                </label>
              ))}
            </div>

            {error && <p className="auth-error" role="alert">{error}</p>}

            <footer className="character-form-actions">
              <button
                className="secondary-button"
                type="button"
                onClick={onCancel}
                disabled={saving}
              >
                Cancel
              </button>
              <button
                className="primary-button"
                type="submit"
                disabled={saving || loadingOptions}
              >
                {saving ? 'Creating…' : '✦ Create character'}
              </button>
            </footer>
          </form>
        )}
      </section>
    </div>
  )
}

export default CreateCharacterForm
