from seed.backgrounds import seed_backgrounds
from seed.classes import seed_classes
from seed.races import seed_races
from seed.spells import seed_spells


def main():
    seed_races()
    seed_classes()
    seed_backgrounds()
    seed_spells()

    print("All seeds completed successfully!")


if __name__ == "__main__":
    main()
    