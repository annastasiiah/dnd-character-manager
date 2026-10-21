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

const SPELL_LEVELS = [
  { value: '', label: 'Усі рівні' },
  { value: '0', label: 'Заговір' },
  { value: '1', label: '1-й рівень' },
  { value: '2', label: '2-й рівень' },
  { value: '3', label: '3-й рівень' },
  { value: '4', label: '4-й рівень' },
  { value: '5', label: '5-й рівень' },
  { value: '6', label: '6-й рівень' },
  { value: '7', label: '7-й рівень' },
  { value: '8', label: '8-й рівень' },
  { value: '9', label: '9-й рівень' },
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

  const [loadingCharacterSpells, setLoadingCharacterSpells] =
    useState(true)
  const [loadingCatalogue, setLoadingCatalogue] = useState(true)

  const [busySpellId, setBusySpellId] = useState<number | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadCharacterSpells() {
      setLoadingCharacterSpells(true)

      try {
        const spells = await getCharacterSpells(token, characterId)

        if (!cancelled) {
          setCharacterSpells(spells)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Не вдалося завантажити заклинання персонажа.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoadingCharacterSpells(false)
        }
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
            search: search.trim(),
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
        if (!cancelled) {
          setLoadingCatalogue(false)
        }
      }
    }

    void loadCatalogue()

    return () => {
      cancelled = true
    }
  }, [search, level, school])

  async function handleAddSpell(spell: Spell) {
    if (characterSpells.some((item) => item.id === spell.id)) {
      return
    }

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

  const spellsByLevel = characterSpells.reduce<Record<string, number>>(
    (result, spell) => {
      const label =
        spell.level === 0 ? 'Заговори' : `${spell.level}-й рівень`

      result[label] = (result[label] ?? 0) + 1
      return result
    },
    {},
  )

  return (
    <div className="character-spells">
      {error && (
        <div className="character-spells-error" role="alert">
          <p>{error}</p>
          <button type="button" onClick={() => setError('')}>
            Закрити
          </button>
        </div>
      )}

      <section className="known-spells">
        <header className="spells-section-heading">
          <div>
            <p className="spells-eyebrow">ТВОЯ КНИГА МАГІЇ</p>
            <h3>Заклинання персонажа</h3>
            <p>Усього відомих заклинань: {characterSpells.length}</p>
          </div>
        </header>

        {!loadingCharacterSpells && characterSpells.length > 0 && (
          <div className="spell-level-summary">
            {Object.entries(spellsByLevel).map(([label, count]) => (
              <div className="spell-level-summary-item" key={label}>
                <span>{label}</span>
                <strong>{count}</strong>
              </div>
            ))}
          </div>
        )}

        {loadingCharacterSpells ? (
          <p className="spells-message" role="status">
            Завантаження заклинань персонажа…
          </p>
        ) : characterSpells.length === 0 ? (
          <div className="spells-empty">
            <h4>Книга магії поки порожня</h4>
            <p>
              Знайди потрібні заклинання в каталозі нижче та додай їх
              персонажу.
            </p>
          </div>
        ) : (
          <div className="character-spell-list">
            {characterSpells.map((spell) => (
              <article className="character-spell-card" key={spell.id}>
                <div className="character-spell-info">
                  <h4>{spell.name}</h4>

                  <div className="spell-metadata">
                    <span>
                      {spell.level === 0
                        ? 'Заговір'
                        : `Рівень ${spell.level}`}
                    </span>
                    <span>{spell.school}</span>
                  </div>

                  <p className="spell-details">
                    <span>Час накладання:</span> {spell.casting_time}
                  </p>

                  <p className="spell-details">
                    <span>Дистанція:</span> {spell.spell_range}
                  </p>

                  <p className="spell-details">
                    <span>Тривалість:</span> {spell.duration}
                  </p>

                  {spell.description && (
                    <p className="spell-description">
                      {spell.description}
                    </p>
                  )}
                </div>

                <button
                  type="button"
                  className="spell-remove-button"
                  disabled={busySpellId !== null}
                  onClick={() => void handleRemoveSpell(spell)}
                  aria-label={`Видалити заклинання ${spell.name}`}
                >
                  {busySpellId === spell.id
                    ? 'Обробка…'
                    : 'Видалити'}
                </button>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="spell-catalogue">
        <header className="spells-section-heading">
          <div>
            <p className="spells-eyebrow">КОМПЕНДІУМ</p>
            <h3>Каталог заклинань</h3>
            <p>Досліджуй магію та обирай нові заклинання.</p>
          </div>

          <span className="spell-catalogue-count">
            {loadingCatalogue ? '…' : availableSpells.length}
          </span>
        </header>

        <div className="character-spell-filters">
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Шукати заклинання…"
            aria-label="Пошук заклинань за назвою"
          />

          <select
            value={level}
            onChange={(event) => setLevel(event.target.value)}
            aria-label="Фільтр за рівнем заклинання"
          >
            {SPELL_LEVELS.map((item) => (
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

        {loadingCatalogue ? (
          <p className="spells-message" role="status">
            Завантаження каталогу…
          </p>
        ) : availableSpells.length === 0 ? (
          <div className="spells-empty">
            <h4>Заклинань не знайдено</h4>
            <p>
              Спробуй змінити пошуковий запит або вибрати інші фільтри.
            </p>

            {(search || level || school) && (
              <button
                type="button"
                className="spell-reset-filters"
                onClick={() => {
                  setSearch('')
                  setLevel('')
                  setSchool('')
                }}
              >
                Скинути фільтри
              </button>
            )}
          </div>
        ) : (
          <div className="available-spell-list">
            {availableSpells.map((spell) => {
              const alreadyAdded = characterSpellIds.has(spell.id)
              const isBusy = busySpellId === spell.id

              return (
                <article className="available-spell-card" key={spell.id}>
                  <div className="character-spell-info">
                    <h4>{spell.name}</h4>

                    <div className="spell-metadata">
                      <span>
                        {spell.level === 0
                          ? 'Заговір'
                          : `Рівень ${spell.level}`}
                      </span>
                      <span>{spell.school}</span>
                    </div>

                    <p className="spell-details">
                      <span>Час накладання:</span> {spell.casting_time}
                    </p>

                    <p className="spell-details">
                      <span>Дистанція:</span> {spell.spell_range}
                    </p>

                    <p className="spell-details">
                      <span>Тривалість:</span> {spell.duration}
                    </p>

                    <p className="spell-description">
                      {spell.description || 'Опис відсутній.'}
                    </p>
                  </div>

                  <button
                    type="button"
                    className="spell-add-button"
                    disabled={alreadyAdded || busySpellId !== null}
                    onClick={() => void handleAddSpell(spell)}
                    aria-label={
                      alreadyAdded
                        ? `${spell.name} вже додано`
                        : `Додати ${spell.name} персонажу`
                    }
                  >
                    {alreadyAdded
                      ? 'Додано'
                      : isBusy
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