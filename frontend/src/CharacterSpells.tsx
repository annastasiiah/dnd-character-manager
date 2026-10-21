
import { useEffect, useState } from 'react'
import {
  getCharacterSpells,
  getSpells,
  getSpellSchools,
  addCharacterSpell,
  removeCharacterSpell,
} from './api/client'
import type { Spell } from './api/client'
import './CharacterSpells.css'

type CharacterSpellsProps = {
  token: string
  characterId: number
}

const spellLevels = [
  { value: '', label: 'Усі рівні' },
  { value: '0', label: 'Заговір' },
  { value: '1', label: 'Рівень 1' },
  { value: '2', label: 'Рівень 2' },
  { value: '3', label: 'Рівень 3' },
  { value: '4', label: 'Рівень 4' },
  { value: '5', label: 'Рівень 5' },
  { value: '6', label: 'Рівень 6' },
  { value: '7', label: 'Рівень 7' },
  { value: '8', label: 'Рівень 8' },
  { value: '9', label: 'Рівень 9' },
]

export default function CharacterSpells({
  token,
  characterId,
}: CharacterSpellsProps) {
  const [characterSpells, setCharacterSpells] = useState<Spell[]>([])
  const [availableSpells, setAvailableSpells] = useState<Spell[]>([])
  const [schools, setSchools] = useState<string[]>([])
  const [search, setSearch] = useState('')
  const [level, setLevel] = useState('')
  const [school, setSchool] = useState('')
  const [loadingCharacterSpells, setLoadingCharacterSpells] = useState(true)
  const [loadingCatalogue, setLoadingCatalogue] = useState(true)
  const [busySpellId, setBusySpellId] = useState<number | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadCharacterSpells() {
      setLoadingCharacterSpells(true)
      setError('')

      try {
        const result = await getCharacterSpells(token, characterId)
        if (!cancelled) setCharacterSpells(result)
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Не вдалося завантажити заклинання персонажа.',
          )
        }
      } finally {
        if (!cancelled) setLoadingCharacterSpells(false)
      }
    }

    void loadCharacterSpells()

    return () => {
      cancelled = true
    }
  }, [token, characterId])

  useEffect(() => {
    let cancelled = false

    async function loadCatalogue() {
      setLoadingCatalogue(true)

      try {
        const [spellResult, schoolResult] = await Promise.all([
          getSpells({
            search,
            level: level === '' ? undefined : Number(level),
            school: school || undefined,
            limit: 100,
          }),
          getSpellSchools(),
        ])

        if (!cancelled) {
          setAvailableSpells(spellResult.items)
          setSchools(schoolResult)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Не вдалося завантажити каталог заклинань.',
          )
        }
      } finally {
        if (!cancelled) setLoadingCatalogue(false)
      }
    }

    void loadCatalogue()

    return () => {
      cancelled = true
    }
  }, [search, level, school])

  async function handleAddSpell(spell: Spell) {
    setBusySpellId(spell.id)
    setError('')

    try {
      const addedSpell = await addCharacterSpell(
        token,
        characterId,
        spell.id,
      )

      setCharacterSpells((current) =>
        current.some((item) => item.id === addedSpell.id)
          ? current
          : [...current, addedSpell],
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Не вдалося додати заклинання.',
      )
    } finally {
      setBusySpellId(null)
    }
  }

  async function handleRemoveSpell(spell: Spell) {
    setBusySpellId(spell.id)
    setError('')

    try {
      await removeCharacterSpell(token, characterId, spell.id)
      setCharacterSpells((current) =>
        current.filter((item) => item.id !== spell.id),
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Не вдалося видалити заклинання.',
      )
    } finally {
      setBusySpellId(null)
    }
  }

  const characterSpellIds = new Set(
    characterSpells.map((spell) => spell.id),
  )

  return (
    <div className="character-spells">
      <section className="known-spells">
        <div className="spells-section-heading">
          <div>
            <h3>Заклинання персонажа</h3>
            <p>Відомі заклинання: {characterSpells.length}</p>
          </div>
        </div>

        {loadingCharacterSpells ? (
          <p className="spells-message">Завантаження заклинань…</p>
        ) : characterSpells.length === 0 ? (
          <p className="spells-empty">
            Поки що немає заклинань. Знайди потрібні нижче та додай їх.
          </p>
        ) : (
          <div className="character-spell-list">
            {characterSpells.map((spell) => (
              <article className="character-spell-card" key={spell.id}>
                <div className="character-spell-info">
                  <strong>{spell.name}</strong>
                  <span>
                    {spell.level === 0 ? 'Заговір' : `Рівень ${spell.level}`}
                    {' · '}
                    {spell.school}
                  </span>
                  <small>
                    {spell.casting_time} · {spell.spell_range} · {spell.duration}
                  </small>
                </div>

                <button
                  type="button"
                  className="spell-remove-button"
                  disabled={busySpellId !== null}
                  onClick={() => void handleRemoveSpell(spell)}
                >
                  {busySpellId === spell.id ? '…' : 'Видалити'}
                </button>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="spell-catalogue">
        <div className="spells-section-heading">
          <div>
            <h3>Каталог заклинань</h3>
            <p>Знайди заклинання та додай його персонажу</p>
          </div>
        </div>

        <div className="character-spell-filters">
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Пошук за назвою…"
            aria-label="Пошук заклинань"
          />

          <select
            value={level}
            onChange={(event) => setLevel(event.target.value)}
            aria-label="Фільтр за рівнем"
          >
            {spellLevels.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>

          <select
            value={school}
            onChange={(event) => setSchool(event.target.value)}
            aria-label="Фільтр за школою магії"
          >
            <option value="">Усі школи магії</option>
            {schools.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <p className="character-spells-error" role="alert">
            {error}
          </p>
        )}

        {loadingCatalogue ? (
          <p className="spells-message">Завантаження каталогу…</p>
        ) : availableSpells.length === 0 ? (
          <p className="spells-empty">
            Заклинань за цими критеріями не знайдено.
          </p>
        ) : (
          <div className="available-spell-list">
            {availableSpells.map((spell) => {
              const alreadyAdded = characterSpellIds.has(spell.id)

              return (
                <article className="available-spell-card" key={spell.id}>
                  <div className="character-spell-info">
                    <strong>{spell.name}</strong>
                    <span>
                      {spell.level === 0 ? 'Заговір' : `Рівень ${spell.level}`}
                      {' · '}
                      {spell.school}
                    </span>
                    <small>{spell.casting_time} · {spell.spell_range}</small>
                    <p>{spell.description}</p>
                  </div>

                  <button
                    type="button"
                    className="spell-add-button"
                    disabled={alreadyAdded || busySpellId !== null}
                    onClick={() => void handleAddSpell(spell)}
                  >
                    {alreadyAdded
                      ? 'Додано'
                      : busySpellId === spell.id
                        ? 'Додавання…'
                        : '+ Додати'}
                  </button>
                </article>
              )
            })}
          </div>
        )}
      </section>
    </div>
  )
}
