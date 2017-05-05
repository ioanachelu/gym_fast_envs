import numpy as np
import random
import itertools
import scipy.ndimage
import scipy.misc
import time
import tkinter
from PIL import Image
from PIL import ImageTk
import numpy as np
from PIL import Image

class gameOb():
    def __init__(self, coordinates, size, color, reward, name):
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.size = size
        self.color = color
        self.reward = reward
        self.name = name


class Gridworld_2rooms():
    def __init__(self, partial, size, nb_apples=1, nb_oranges=1, orange_reward=0, seed=None, max_steps=400, internal_render=False):
        self.sizeX = size
        self.sizeX_rooms = 2*size + 1
        self.sizeY = size
        self.actions = 4
        self.max_apples = self.sizeX - 1
        self.max_oranges = self.sizeX - 1
        self.nb_apples = nb_apples
        self.nb_oranges = nb_oranges
        self.objects = []
        self.orange_reward = orange_reward
        self.partial = partial
        self.bg = np.zeros([self.sizeY, self.sizeX_rooms])
        self.seed = seed
        self.max_steps = max_steps
        self.non_matching_goal = -1


        # if internal_render:
        self.win = tkinter.Toplevel()

        screen_width = self.win.winfo_screenwidth()
        screen_height = self.win.winfo_screenheight()

        # calculate position x and y coordinates
        x = screen_width + 100
        y = screen_height + 100

        self.win.geometry('+%d+%d' % (200, 400))
        self.win.title("Gridworld")
        # self.win.bind("<Button>", button_click_exit_mainloop)
        self.old_screen_label = None

        if seed:
            np.random.seed(self.seed)
        a = self.reset()
        # plt.imshow(a_big, interpolation="nearest")

    def get_screen(self):
        state, state_big = self.renderEnv()
        return state_big

    def set_seed(self, seed):
        self.seed = seed

    def getFeatures(self):
        return np.array([self.objects[0].x, self.objects[0].y]) / float(self.sizeX)

    def block_position(self, b):
        position = (self.sizeX, b)
        return position

    def reset(self):
        while True:
            apple_color = [np.random.uniform(), np.random.uniform(), np.random.uniform()]
            if apple_color != [0, 0, 1] or apple_color[0] != [1, 1, 0]:
                break

        self.objects = []
        self.block_color = [1, 1, 1]
        self.apple_color = apple_color
        self.orange_color = [1 - a for a in self.apple_color]
        self.orientation = 0
        self.hero = gameOb(self.newPosition(0), 1, [0, 0, 1], None, 'hero')
        self.objects.append(self.hero)
        for i in range(self.nb_apples):
            apple = gameOb(self.newPosition(0), 1, self.apple_color, 1, 'apple')
            self.objects.append(apple)
            apple = gameOb(self.newPosition(0, True), 1, self.orange_color, 1, 'apple_2room')
            self.objects.append(apple)
        for i in range(self.nb_oranges):
            orange = gameOb(self.newPosition(0), 1, self.orange_color, self.orange_reward, 'orange')
            self.objects.append(orange)
            orange = gameOb(self.newPosition(0, True), 1, self.apple_color, self.orange_reward, 'orange_2room')
            self.objects.append(orange)
        for i in range(self.sizeY):
            if i == self.sizeY // 2:
                continue
            block = gameOb(self.block_position(i), 1, self.block_color, self.block_color, 'block')
            self.objects.append(block)
        state, s_big = self.renderEnv()
        self.state = state

        for ob in self.objects:
            if ob.name == 'apple':
                zagoal = ob
                break

        return state, None, None, {"goal": (zagoal.y, zagoal.x), "hero": (self.hero.y, self.hero.x), "grid": (self.sizeY, self.sizeX)}

    def moveChar(self, action):
        # 0 - up, 1 - down, 2 - left, 3 - right, 4 - 90 counter-clockwise, 5 - 90 clockwise
        hero = self.objects[0]
        blockPositions = [[-1, -1]]
        for ob in self.objects:
            if ob.name == 'block': blockPositions.append([ob.x, ob.y])
        blockPositions = np.array(blockPositions)
        heroX = hero.x
        heroY = hero.y
        penalize = 0.
        if action < 4:
            if self.orientation == 0:
                direction = action
            if self.orientation == 1:
                if action == 0:
                    direction = 1
                elif action == 1:
                    direction = 0
                elif action == 2:
                    direction = 3
                elif action == 3:
                    direction = 2
            if self.orientation == 2:
                if action == 0:
                    direction = 3
                elif action == 1:
                    direction = 2
                elif action == 2:
                    direction = 0
                elif action == 3:
                    direction = 1
            if self.orientation == 3:
                if action == 0:
                    direction = 2
                elif action == 1:
                    direction = 3
                elif action == 2:
                    direction = 1
                elif action == 3:
                    direction = 0

            if direction == 0 and hero.y >= 1 and [hero.x, hero.y - 1] not in blockPositions.tolist():
                hero.y -= 1
            if direction == 1 and hero.y <= self.sizeY - 2 and [hero.x, hero.y + 1] not in blockPositions.tolist():
                hero.y += 1
            if direction == 2 and hero.x >= 1 and [hero.x - 1, hero.y] not in blockPositions.tolist():
                hero.x -= 1
            if direction == 3 and hero.x <= self.sizeX - 2 and [hero.x + 1, hero.y] not in blockPositions.tolist():
                hero.x += 1
        if hero.x == heroX and hero.y == heroY:
            penalize = 0.0
        self.objects[0] = hero
        return penalize

    def newPosition(self, sparcity, room_2=False):
        iterables = [list(range(self.sizeX)), list(range(self.sizeY))]
        points = []
        for t in itertools.product(*iterables):
            points.append(t)
        for objectA in self.objects:
            if (objectA.x, objectA.y) in points: points.remove((objectA.x, objectA.y))
        location = np.random.choice(list(range(len(points))), replace=False)
        if room_2:
            x, y = points[location]
            x += self.sizeX
            return (x, y)
        return points[location]

    def checkGoal(self):
        hero = self.objects[0]
        fruits = self.objects[1:]
        ended = False
        for fruit in fruits:
            if hero.x == fruit.x and hero.y == fruit.y and hero != fruit:
                self.objects.remove(fruit)
                if fruit.reward == 1:
                    self.objects.append(gameOb(self.newPosition(0), 1, self.apple_color, 1, 'apple'))
                    return fruit.reward, False
                else:
                    self.objects.append(gameOb(self.newPosition(0), 1, self.orange_color, 0, 'orange'))
                    return fruit.reward, False
        if ended == False:
            return 0.0, False

    def render(self):

        time.sleep(0.1)

        state, state_big = self.renderEnv()

        screen = Image.fromarray(state_big, 'RGB')
        screen = screen.resize((512, 256))

        self.win.geometry('%dx%d' % (screen.size[0], screen.size[1]))

        tkpi = ImageTk.PhotoImage(screen)
        label_img = tkinter.Label(self.win, image=tkpi)
        label_img.place(x=0, y=0,
                        width=screen.size[0], height=screen.size[1])

        # self.win.mainloop()            # wait until user clicks the window
        self.win.update_idletasks()
        self.win.update()

        # import matplotlib.pyplot as plt
        # pil_image = Image.fromarray(state_big)
        # pil_image.show()
        # plt.imshow(state_big)

    def renderEnv(self):
        if self.partial == True:
            padding = 2
            a = np.ones([self.sizeY + (padding * 2), self.sizeX + (padding * 2), 3])
            a[padding:-padding, padding:-padding, :] = 0
            a[padding:-padding, padding:-padding, :] += np.dstack([self.bg, self.bg, self.bg])
        else:
            a = np.zeros([self.sizeY, self.sizeX_rooms, 3])
            padding = 0
            a += np.dstack([self.bg, self.bg, self.bg])
        try:
            hero = self.objects[0]
        except:
            print("fsf")
        for item in self.objects:
            a[item.y + padding:item.y + item.size + padding, item.x + padding:item.x + item.size + padding,
            :] = item.color
            # if item.name == 'hero':
            #    hero = item
        if self.partial == True:
            a = a[(hero.y):(hero.y + (padding * 2) + hero.size), (hero.x):(hero.x + (padding * 2) + hero.size), :]
        a_big = scipy.misc.imresize(a, [200, 400, 3], interp='nearest')
        return a, a_big

    def step(self, action):

        self.max_steps -= 1

        penalty = self.moveChar(action)
        reward, done = self.checkGoal()
        state, s_big = self.renderEnv()

        for ob in self.objects:
            if ob.name == 'apple':
                zagoal = ob
                break

        if self.max_steps == 0:
            done = True

        if reward == None:
            print(done)
            print(reward)
            print(penalty)
            return state, s_big, (reward + penalty), done, {"goal": (zagoal.y, zagoal.x), "hero": (self.hero.y, self.hero.x), "grid": (self.sizeY, self.sizeX)}
        else:
            goal = None
            for ob in self.objects:
                if ob.name == 'apple':
                    goal = ob
            # return state, s_big, (reward + penalty), done, [self.objects[0].y, self.objects[0].x] + [goal.y, goal.x]
            return state, s_big, (reward + penalty), done, {"goal": (zagoal.y, zagoal.x), "hero": (self.hero.y, self.hero.x), "grid": (self.sizeY, self.sizeX)}


if __name__ == '__main__':

    import time
    import tkinter
    from PIL import Image
    from PIL import ImageTk
    import numpy as np

    player_rng = np.random.RandomState(0)
    game = Gridworld_2rooms(partial=False, size=5, nb_apples=1, nb_oranges=1, internal_render=True)

    start = time.time()
    # reward_color = [np.random.uniform(), np.random.uniform(), np.random.uniform()]
    # reward_color = [1,0,0]
    s = game.reset()
    ep = 0
    step = 0
    tot_rw = 0

    while True:
        s1, s1_big, r, d, _ = game.step(player_rng.choice(game.actions))
        step += 1
        game.render()
        tot_rw += r
        if d:
            ep += 1
            s, s_big, _, _ = game.reset()

    print("Finished %d episodes in %d steps in %.2f. Total reward: %d.",
          (ep, step, time.time() - start, tot_rw))



