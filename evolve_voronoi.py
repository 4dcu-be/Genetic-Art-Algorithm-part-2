from PIL import Image
from evol import Evolution, Population

import random
import os
from copy import deepcopy

from voronoi_painting import VoronoiPainting


def score(x: VoronoiPainting) -> float:
    current_score = x.image_diff(x.target_image)
    print(".", end='', flush=True)
    return current_score


def pick_best_and_random(pop, maximize=False):
    evaluated_individuals = tuple(filter(lambda x: x.fitness is not None, pop))
    if len(evaluated_individuals) > 0:
        mom = max(evaluated_individuals, key=lambda x: x.fitness if maximize else -x.fitness)
    else:
        mom = random.choice(pop)
    dad = random.choice(pop)
    return mom, dad


def pick_best(pop, maximize=False):
    evaluated_individuals = tuple(filter(lambda x: x.fitness is not None, pop))
    if len(evaluated_individuals) > 0:
        mom = max(evaluated_individuals, key=lambda x: x.fitness if maximize else -x.fitness)
    else:
        mom = random.choice(pop)
    return mom


def pick_random(pop):
    mom = random.choice(pop)
    dad = random.choice(pop)
    return mom, dad


def mutate_painting(x: VoronoiPainting, rate=0.04, sigma=1) -> VoronoiPainting:
    x.mutate_points(rate=rate, sigma=sigma)
    return deepcopy(x)


def shrink_painting(x: VoronoiPainting) -> VoronoiPainting:
    x.shrink_points()
    return deepcopy(x)


def mate(mom: VoronoiPainting, dad: VoronoiPainting):
    child_a, child_b = VoronoiPainting.mate(mom, dad)

    return deepcopy(child_a)


def clone(mom: VoronoiPainting):
    return deepcopy(mom)


def merge(mom: VoronoiPainting, dad: VoronoiPainting):
    child_a = VoronoiPainting.merge(mom, dad)

    return deepcopy(child_a)


def print_summary(pop, img_template="output%d.png", checkpoint_path="output") -> Population:
    avg_fitness = sum([i.fitness for i in pop.individuals])/len(pop.individuals)
    chromosome_length = pop.individuals[0].chromosome.num_points
    print("\nCurrent generation %d, best score %f, pop. avg. %f. Chromosome length %d" % (pop.generation,
                                                                                          pop.current_best.fitness,
                                                                                          avg_fitness,
                                                                                          chromosome_length))
    img = pop.current_best.chromosome.draw(scale=3)
    img.save(img_template % pop.generation, 'PNG')

    if pop.generation % 50 == 0:
        pop.checkpoint(target=checkpoint_path, method='pickle')

    return pop


if __name__ == "__main__":
    target_image_path = "./img/girl_with_pearl_earring_half.jpg"
    checkpoint_path = "./output/"
    image_template = os.path.join(checkpoint_path, "drawing_%05d.png")
    target_image = Image.open(target_image_path).convert('RGBA')

    num_points = 250
    population_size = 250

    pop = Population(chromosomes=[VoronoiPainting(num_points, target_image, background_color=(128, 128, 128)) for _ in
                                  range(population_size)],
                     eval_function=score, maximize=False, concurrent_workers=4)

    # Code to load a pickled/stored version, each 50 generation the population is written to disk
    # stored_pop = Population.load('./output/20200207-223736.187164.pkl', eval_function=score, maximize=False)
    # # Create new population from stored one, trick to get multiprocessing working after
    # pop = Population(chromosomes=[deepcopy(a) for a in stored_pop.chromosomes],
    #                  eval_function=score, maximize=False, concurrent_workers=4, generation=4550)

    print(f"Staring with {pop.concurrent_workers} workers")

    genome_duplication = (Evolution()
                          .survive(fraction=0.025)
                          .breed(parent_picker=pick_best_and_random, combiner=merge, population_size=population_size)
                          .mutate(mutate_function=mutate_painting, rate=0.05, sigma=0.5)
                          .evaluate(lazy=False)
                          .apply(print_summary,
                                 img_template=image_template,
                                 checkpoint_path=checkpoint_path))

    evo_step_1 = (Evolution()
                  .survive(fraction=0.025)
                  .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
                  .mutate(mutate_function=mutate_painting, rate=0.05, sigma=0.5)
                  .evaluate(lazy=False)
                  .apply(print_summary,
                         img_template=image_template,
                         checkpoint_path=checkpoint_path))

    evo_step_2 = (Evolution()
                  .survive(fraction=0.025)
                  .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
                  .mutate(mutate_function=mutate_painting, rate=0.03, sigma=0.4)
                  .evaluate(lazy=False)
                  .apply(print_summary,
                         img_template=image_template,
                         checkpoint_path=checkpoint_path))

    evo_step_3 = (Evolution()
                  .survive(fraction=0.025)
                  .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
                  .mutate(mutate_function=mutate_painting, rate=0.005, sigma=0.4)
                  .evaluate(lazy=False)
                  .apply(print_summary,
                         img_template=image_template,
                         checkpoint_path=checkpoint_path))

    shrink_step = (Evolution()
                   .survive(n=1)
                   .breed(parent_picker=pick_best, combiner=clone, population_size=population_size)
                   .mutate(mutate_function=shrink_painting)
                   .evaluate(lazy=False)
                   .apply(print_summary,
                          img_template=image_template,
                          checkpoint_path=checkpoint_path))

    # 250 points
    pop = pop.evolve(evo_step_1, n=999)
    pop = pop.evolve(genome_duplication, n=1)
    # 500 points
    pop = pop.evolve(evo_step_1, n=899)
    pop = pop.evolve(shrink_step, n=100)
    pop = pop.evolve(genome_duplication, n=1)
    # 800 points
    pop = pop.evolve(evo_step_2, n=900)
    pop = pop.evolve(shrink_step, n=100)
    pop = pop.evolve(evo_step_2, n=900)
    pop = pop.evolve(shrink_step, n=100)
    pop = pop.evolve(evo_step_3, n=1000)
