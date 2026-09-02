from seed_backgrounds import seed_backgrounds
from seed_classes import seed_classes
from seed_races import seed_races
from seed_spells import seed_spells


def main():
    seed_races()
    seed_classes()
    seed_backgrounds()
    seed_spells()

    print("All seeds completed successfully!")


if __name__ == "__main__":
    main()