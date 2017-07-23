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

def uniq(lst):
    last = object()
    for item in lst:
        if item == last:
            continue
        yield item
        last = item

class Gridworld_4Rooms():
    def __init__(self, partial, seed=None, deterministic=False, internal_render=False):
        self.room_sizes = [[7, 7], [7, 7], [7, 7], [7, 7]]
        self.actions = 4
        self.deterministic = deterministic

        self.objects = []
        self.partial = partial
        self.bg = [np.zeros([size_y, size_x]) for size_y, size_x in self.room_sizes]
        self.seed = seed
        self.crt_room = 0
        self.rooms = [0, 1, 2, 3]
        self.gateways = [[[2, 0], [6, 4]], [[0, 4], [3, 0]], [[2, 6], [6, 3]], [[0, 3], [3, 6]]]
        self.move_to = [[[2, (2, 6)], [1, (0, 4)]], [[0, (6, 4)], [3, (3, 6)]], [[0, (2, 0)], [3, (0, 3)]], [[2, (6, 3)], [1, (3, 0)]]]
        self.goal_locations = [(x, y) for x in range(1, self.room_sizes[0][0] - 1) for y in range(1, self.room_sizes[0][1] - 1)]


        self.block_positions = []
        for r in self.rooms:
            block_positions = []
            block_positions.extend([[0, x] for x in range(self.room_sizes[r][1])])
            block_positions.extend([[self.room_sizes[r][0] - 1, x] for x in range(self.room_sizes[r][1])])
            block_positions.extend([[y, 0] for y in range(self.room_sizes[r][0])])
            block_positions.extend([[y, self.room_sizes[r][1] - 1] for y in range(self.room_sizes[r][0])])

            block_positions.remove(self.gateways[r][0])
            block_positions.remove(self.gateways[r][1])
            block_positions = list(uniq(block_positions))
            self.block_positions.append(block_positions)

        if self.deterministic:
            self.goal_room = 3
        else:
            self.goal_room = np.random.choice(self.rooms, replace=False)

        if self.deterministic:
            self.goal_location = (4, 2)
        else:
            self.goal_location = self.goal_locations[np.random.randint(len(self.goal_locations), size=1)[0]]
            # self.goal_location = np.random.choice(self.goal_locations, replace=False)

        # if internal_render:
        self.win = tkinter.Toplevel()

        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()

        # calculate position x and y coordinates
        # x = screen_width + 100
        # y = screen_height + 100
        # ('%dx%d%+d+%d' % (sw, sh, sw, 0))
        # self.win.geometry('+%d+%d' % ((screen_width - 200)/2, (screen_height - 200)/2))
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        w = self.room_sizes[self.crt_room][0] * 40
        h = self.room_sizes[self.crt_room][1] * 40
        a, b = (sw - w) / 2, (sh - h) / 2
        self.win.geometry('%dx%d%+d+%d' % (sw, sh, a, b))
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

    def reset(self):
        if self.deterministic:
            location = (1, 5)
        else:
           location = self.newPosition(0)
        self.crt_room = 0
        self.objects = []
        self.orientation = 0
        self.hero = gameOb(location, 1, [0, 0, 1], None, 'hero')

        if self.deterministic:
            self.goal_room = 3
        else:
            self.goal_room = np.random.choice(self.rooms, replace=False)

        if self.deterministic:
            self.goal_location = (4, 2)
        else:
            self.goal_location = self.goal_locations[np.random.randint(len(self.goal_locations), size=1)[0]]

        if self.crt_room == self.goal_room:
            self.goal = gameOb(self.goal_location, 1, [1, 0, 0], None, 'goal')
            self.objects.append(self.goal)

        self.objects.append(self.hero)
        for bp in self.block_positions[self.crt_room]:
            self.objects.append(gameOb(bp, 1, [0.5, 0.5, 0.5], None, 'block'))
        state, s_big = self.renderEnv()
        self.state = state

        return state, None, None, {} #{"goal": (self.teleporter.y, self.teleporter.x), "hero": (self.hero.y, self.hero.x), "grid": (self.sizeY, self.sizeX)}

    def moveChar(self, action):
        # 0 - up, 1 - down, 2 - left, 3 - right, 4 - 90 counter-clockwise, 5 - 90 clockwise
        hero = self.objects[0]
        # blockPositions = [[-1, -1]]
        # for ob in self.objects:
        #     if ob.name == 'block': blockPositions.append([ob.x, ob.y])
        blockPositions = np.array(self.block_positions[self.crt_room])
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
            if direction == 1 and hero.y <= self.room_sizes[self.crt_room][1] - 2 and [hero.x, hero.y + 1] not in blockPositions.tolist():
                hero.y += 1
            if direction == 2 and hero.x >= 1 and [hero.x - 1, hero.y] not in blockPositions.tolist():
                hero.x -= 1
            if direction == 3 and hero.x <= self.room_sizes[self.crt_room][0] - 2 and [hero.x + 1, hero.y] not in blockPositions.tolist():
                hero.x += 1
        if hero.x == heroX and hero.y == heroY:
            penalize = 0.0
        self.objects[0] = hero
        return penalize

    def newPosition(self, sparcity):
        iterables = [list(range(1, self.room_sizes[self.crt_room][0] - 1)), list(range(1, self.room_sizes[self.crt_room][1] - 1))]
        points = []
        for t in itertools.product(*iterables):
            points.append(t)
        for objectA in self.objects:
            if (objectA.x, objectA.y) in points: points.remove((objectA.x, objectA.y))
        location = np.random.choice(list(range(len(points))), replace=False)
        return points[location]

    def checkGoal(self):
        hero = self.objects[0]

        for i, gate in enumerate(self.gateways[self.crt_room]):
            if hero.x == gate[0] and hero.y == gate[1]:
                self.move_to_next_room(i)

        if self.crt_room == self.goal_room and hero.x == self.goal_location[0] and hero.y == self.goal_location[1]:
            for ob in self.objects:
                if ob.name == 'goal':
                    self.objects.remove(ob)
                    break
            return 100.0, True

        return -1.0, False

    def move_to_next_room(self, i):
        self.crt_room, next_hero_pos = self.move_to[self.crt_room][i]
        self.objects = self.objects[:1]
        self.objects[0].x, self.objects[0].y = next_hero_pos
        for bp in self.block_positions[self.crt_room]:
            self.objects.append(gameOb(bp, 1, [0.5, 0.5, 0.5], None, 'block'))
        if self.crt_room == self.goal_room:
            self.goal = gameOb(self.goal_location, 1, [1, 0, 0], None, 'goal')
            self.objects.append(self.goal)

    def render(self):

        time.sleep(0.1)

        state, state_big = self.renderEnv()

        screen = Image.fromarray(state_big, 'RGB')
        screen = screen.resize((self.room_sizes[self.crt_room][0] * 40, self.room_sizes[self.crt_room][1] * 40))

        # self.win.geometry('%dx%d' % (screen.size[0], screen.size[1]))
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        w = self.room_sizes[self.crt_room][0] * 40
        h = self.room_sizes[self.crt_room][1] * 40
        a, b = (sw - w) / 2, (sh - h) / 2
        self.win.geometry('%dx%d%+d+%d' % (sw, sh, a, b))

        # screen = Image.fromarray(state, 'RGB')
        # screen = screen.resize((self.room_sizes[self.crt_room][0], self.room_sizes[self.crt_room][1]))
        #
        # # self.win.geometry('%dx%d' % (screen.size[0], screen.size[1]))
        # sw = self.win.winfo_screenwidth()
        # sh = self.win.winfo_screenheight()
        # w = self.room_sizes[self.crt_room][0]
        # h = self.room_sizes[self.crt_room][1]
        # a, b = (sw - w) / 2, (sh - h) / 2
        # self.win.geometry('%dx%d%+d+%d' % (sw, sh, a, b))

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
            a = np.zeros([self.room_sizes[self.crt_room][0], self.room_sizes[self.crt_room][1], 3])
            padding = 0
            a += np.dstack([self.bg[self.crt_room], self.bg[self.crt_room], self.bg[self.crt_room]])
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
        # orig_image = Image.fromarray(a, "RGB")
        # orig_image = orig_image.resize((self.room_sizes[self.crt_room][0] * 40, self.room_sizes[self.crt_room][1] * 40), Image.NEAREST)
        # a_big = list(orig_image.getdata())
        a_big = scipy.misc.imresize(a * 255, [self.room_sizes[self.crt_room][0] * 40, self.room_sizes[self.crt_room][1] * 40, 3], interp='nearest')
        # a_big = cv2.resize(a, (self.room_sizes[self.crt_room][0] * 40, self.room_sizes[self.crt_room][1] * 40), 0, 0, cv2.INTER_LINEAR)

        # a_big = np.array(orig_image.getdata(), dtype=np.uint8)
        # a_big = a_big.reshape((orig_image.size[1], orig_image.size[0], 3))
        return a, a_big

    def step(self, action):
        penalty = self.moveChar(action)
        reward, done = self.checkGoal()
        state, s_big = self.renderEnv()

        if reward == None:
            print(done)
            print(reward)
            print(penalty)
            if done:
                return state, s_big, (reward + penalty), done, {}
            return state, (reward + penalty), done, {} #{"goal": (zagoal.y, zagoal.x), "hero": (self.hero.y, self.hero.x), "grid": (self.sizeY, self.sizeX)}
        else:

            if done:
                return state, s_big, (reward + penalty), done, {}
            # return state, s_big, (reward + penalty), done, [self.objects[0].y, self.objects[0].x] + [goal.y, goal.x]
            return state, s_big, (reward + penalty), done, {}#{"goal": (zagoal.y, zagoal.x), "hero": (self.hero.y, self.hero.x), "grid": (self.sizeY, self.sizeX)}


if __name__ == '__main__':

    import time
    import tkinter
    from PIL import Image
    from PIL import ImageTk
    import numpy as np

    player_rng = np.random.RandomState(0)
    game = Gridworld_4Rooms(partial=False, internal_render=True, deterministic=False)

    start = time.time()
    s = game.reset()
    game.render()
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
            s = game.reset()
            print("TOTAL REWARD {}".format(tot_rw))
            tot_rw = 0

    print("Finished %d episodes in %d steps in %.2f. Total reward: %d.",
          (ep, step, time.time() - start, tot_rw))



