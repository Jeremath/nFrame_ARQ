import pygame
import sys
import threading

'''组员：
    1. 丁友涛
    2. 邹珂琳
    实现了回退n帧协议模拟，我们组的思路是利用pygame库的交互效果模拟数据链路层帧传递可能遇到的所有情况：
    1. 按下键盘上的按键“1”，模拟发送方发送有效帧，接收方收到有效帧并发送ACK。
    2. 按下键盘上的按键“2”，模拟发送方发送一个帧，但在传递过程中帧丢失或者损坏，接收方无法确认且不发送ACK。
    3. 按下键盘上的按键“3”，模拟发送方发送一个帧，接收方接受到有效帧并回复ACK，但是由于ACK丢失或损坏导致发送方无法接收ACK
    在整个过程中我们利用了定时器进行超时处理，设置阈值为5s，当超时条件触发后，重发所有帧。
    并且我们这里为了演示效果，设置窗口大小为5，当发送窗口缓存满时，提示无法再发送帧。
    发送方具备累计确认的功能，当接收到ACK时，Sf会根据cunt值进行移动，实现累计确认功能。
    接收方在没有收到有效帧时不回复ACK，并且当收到有效帧后交付有效帧。'''

pygame.init()

WIDTH, HEIGHT = 900, 700
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("回退n帧协议模拟")

FONT_SIZE = 20
BIG_FONT_SIZE = 24
FONT = pygame.font.SysFont('Arial', FONT_SIZE)
BIG_FONT = pygame.font.SysFont('Arial', BIG_FONT_SIZE)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

MAX_SEQ = 16
WINDOW_SIZE_SENDER = 5
WINDOW_SIZE_RECEIVER = 1

# 网络层方块的位置和大小实现交付有效帧功能
NETWORK_LAYER_RECT = pygame.Rect(350, 500, 100, 100)
NETWORK_LAYER_CENTER = (NETWORK_LAYER_RECT.centerx, NETWORK_LAYER_RECT.centery)

class Sender:
    def __init__(self):
        self.Sf = 0
        self.Sn = 0
        self.Timefalg = 0
        self.cunt = 1
        self.window_size = WINDOW_SIZE_SENDER

    def can_send(self):
        return (self.Sn - self.Sf) % MAX_SEQ < self.window_size

    def set_sn_to_sf(self):
        self.Sn = self.Sf
        self.Timefalg = 0
        print("Timeout!!!!!!!!!!!!!!!!!!!!!!!!")

    #成帧发送
    def send_frame(self, key_pressed):
        message = ""
        if not self.can_send():
            message = "Send window is full. Cannot send. Timeout all the frames need resend."
            self.Sn = self.Sf
            print(message)
            return message

        frame_num = self.Sn
        print(f"Sending frame: {frame_num} with key: {key_pressed}")

        self.Sn = (self.Sn + 1) % MAX_SEQ
        print(f"Sn incremented to: {self.Sn}")

        if key_pressed == 1:
            if not self.can_send():
                self.Sn = self.Sf
            return f"Sent valid frame {frame_num}. Waiting for animations..."

        elif key_pressed == 2:
            if not self.can_send():
                self.Sn = self.Sf
            if (self.Timefalg == 0):
                self.Timefalg = 1
                timer = threading.Timer(5.0, self.set_sn_to_sf)
                timer.start()
            print("Sent corrupt frame. Sf and Rn remain unchanged.")
            return "Sent corrupt frame. Sf and Rn unchanged."

        elif key_pressed == 3:
            if not self.can_send():
                self.Sn = self.Sf
            # 这里增加cunt，标记下如果以后有ACK的话就会以cunt步长移动Sf，这里是为了能实现累计确认功能
            self.cunt += 1
            print("Sent valid frame (no ACK scenario). Sf unchanged.")
            return f"Sent valid frame {frame_num}. Waiting for animations..."

        else:
            return "Unknown key pressed."


class Receiver:
    def __init__(self):
        self.Rn = 0
        self.window_size = WINDOW_SIZE_RECEIVER

    def receive_ack(self, key_pressed, sn_prev):
        message = ""
        if key_pressed == 2:
            print("Receiver received corrupt frame. No ACK sent.")
            message = "Receiver received corrupt frame. No ACK sent."
        return message


def draw_queue(start_x, start_y, sequence_numbers, window_start, window_size, title, sf=None, sn=None):
    for i in range(MAX_SEQ):
        x = start_x + i * 40
        y = start_y
        rect = pygame.Rect(x, y, 35, 35)
        pygame.draw.rect(WINDOW, BLACK, rect, 2)

        if window_start + window_size <= MAX_SEQ:
            if window_start <= i < window_start + window_size:
                pygame.draw.rect(WINDOW, YELLOW, rect)
                pygame.draw.rect(WINDOW, BLACK, rect, 2)
        else:
            if i >= window_start or i < (window_start + window_size) % MAX_SEQ:
                pygame.draw.rect(WINDOW, YELLOW, rect)
                pygame.draw.rect(WINDOW, BLACK, rect, 2)

        num_text = FONT.render(str(sequence_numbers[i]), True, BLACK)
        text_rect = num_text.get_rect(center=(x + 17, y + 17))
        WINDOW.blit(num_text, text_rect)

        if i == sf or i == sn:
            pygame.draw.rect(WINDOW, RED, rect, 3)

    title_text = BIG_FONT.render(title, True, BLACK)
    WINDOW.blit(title_text, (start_x, start_y - 40))


def display_info(text, pos, color=BLACK):
    info_text = FONT.render(text, True, color)
    WINDOW.blit(info_text, pos)


def draw_network_layer():

    pygame.draw.rect(WINDOW, GRAY, NETWORK_LAYER_RECT)
    pygame.draw.rect(WINDOW, BLACK, NETWORK_LAYER_RECT, 2)
    net_label = BIG_FONT.render("Deliver valid frames", True, BLACK)

    WINDOW.blit(net_label, (NETWORK_LAYER_RECT.x, NETWORK_LAYER_RECT.y - 30))


def main():
    clock = pygame.time.Clock()
    sender = Sender()
    receiver = Receiver()

    sender_seq = list(range(MAX_SEQ))
    receiver_seq = list(range(MAX_SEQ))

    running = True
    message = ""
    message_time = 0
    #这里对动画阶段进行分类，因为我们组思路是根据不同按键实现帧传递过程中的不同情况
    # 动画阶段说明：
    # 0 - 无动画
    # 1 - Sender -> Receiver
    # 2 - Receiver -> Sender (ACK)
    # 3 - Receiver -> Network Layer 
    animation_phase = 0

    animation_start_time = None
    animation_duration = 500  

    current_frame_num = None
    current_key_pressed = None

    ack_frame_num = None
    ack_start_pos = None
    ack_end_pos = None

    forward_start_pos = None
    forward_end_pos = None

    network_start_pos = None
    network_end_pos = None

    sender_start_x, sender_start_y = 50, 150
    receiver_start_x, receiver_start_y = 50, 400

    while running:
        dt = clock.tick(30)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key_pressed = 1
                    if animation_phase == 0:
                        frame_num = sender.Sn
                        result = sender.send_frame(key_pressed)
                        message = result
                        message_time = current_time
                        current_frame_num = frame_num
                        current_key_pressed = key_pressed

                        start_x = sender_start_x + frame_num * 40 + 17
                        start_y = sender_start_y + 17
                        forward_start_pos = (start_x, start_y)

                        end_x = receiver_start_x + receiver.Rn * 40 + 17
                        end_y = receiver_start_y + 17
                        forward_end_pos = (end_x, end_y)

                        animation_phase = 1
                        animation_start_time = current_time

                    else:
                        message = "Wait for the current animation to finish before sending a new valid frame."
                        message_time = current_time

                elif event.key == pygame.K_2:
                    key_pressed = 2
                    sn_prev = sender.Sn
                    result = sender.send_frame(key_pressed)
                    message = result
                    message_time = current_time

                    ack_message = receiver.receive_ack(key_pressed, sn_prev)
                    if ack_message:
                        message += " " + ack_message
                        message_time = current_time

                elif event.key == pygame.K_3:
                    key_pressed = 3
                    if animation_phase == 0:
                        frame_num = sender.Sn
                        result = sender.send_frame(key_pressed)
                        message = result
                        message_time = current_time
                        current_frame_num = frame_num
                        current_key_pressed = key_pressed

                        start_x = sender_start_x + frame_num * 40 + 17
                        start_y = sender_start_y + 17
                        forward_start_pos = (start_x, start_y)

                        end_x = receiver_start_x + receiver.Rn * 40 + 17
                        end_y = receiver_start_y + 17
                        forward_end_pos = (end_x, end_y)

                        animation_phase = 1
                        animation_start_time = current_time
                    else:
                        message = "Wait for the current animation to finish before sending a new valid frame."
                        message_time = current_time

        WINDOW.fill(WHITE)

        draw_queue(50, 150, sender_seq, sender.Sf, sender.window_size, 
                   "Sender Queue (Window Size = 5,MAXSIZE = 2^n-1)", 
                   sf=sender.Sf, sn=sender.Sn)
        draw_queue(50, 400, receiver_seq, receiver.Rn, receiver.window_size, 
                   "Receiver Queue (Window Size = 1)", 
                   sf=None, sn=receiver.Rn)  

        draw_network_layer()

        display_info(f"Sf: {sender.Sf}", (50, 90))
        display_info(f"Sn: {sender.Sn}", (200, 90))
        display_info(f"Rn: {receiver.Rn}", (50, 340))

        if animation_phase == 1:
            elapsed = current_time - animation_start_time
            if elapsed < animation_duration:
                progress = elapsed / animation_duration
                cur_x = forward_start_pos[0] + (forward_end_pos[0] - forward_start_pos[0]) * progress
                cur_y = forward_start_pos[1] + (forward_end_pos[1] - forward_start_pos[1]) * progress

                moving_rect = pygame.Rect(cur_x - 17, cur_y - 17, 35, 35)
                pygame.draw.rect(WINDOW, ORANGE, moving_rect)
                frame_text = FONT.render(str(current_frame_num), True, BLACK)
                frame_text_rect = frame_text.get_rect(center=(cur_x, cur_y))
                WINDOW.blit(frame_text, frame_text_rect)
            else:
                # 动画结束，判断是否是期待帧
                if receiver.Rn == current_frame_num:
                    receiver.Rn = (receiver.Rn + 1) % MAX_SEQ
                    message = f"Receiver received frame {current_frame_num}. Rn incremented."
                    # 帧到达后进入网络层动画
                    animation_phase = 3
                    animation_start_time = current_time
                    network_start_pos = forward_end_pos
                    network_end_pos = NETWORK_LAYER_CENTER

                else:
                    message = f"Receiver got frame {current_frame_num}, but not expected. Rn not incremented."
                    animation_phase = 0

                message_time = current_time

        elif animation_phase == 3:
            elapsed = current_time - animation_start_time
            if elapsed < animation_duration:
                progress = elapsed / animation_duration
                cur_x = network_start_pos[0] + (network_end_pos[0] - network_start_pos[0]) * progress
                cur_y = network_start_pos[1] + (network_end_pos[1] - network_start_pos[1]) * progress

                moving_rect = pygame.Rect(cur_x - 17, cur_y - 17, 35, 35)
                pygame.draw.rect(WINDOW, ORANGE, moving_rect)
                frame_text = FONT.render(str(current_frame_num), True, BLACK)
                frame_text_rect = frame_text.get_rect(center=(cur_x, cur_y))
                WINDOW.blit(frame_text, frame_text_rect)
            else:
                #帧已交付到网络层
                message = f"Frame {current_frame_num} delivered to Network Layer."
                message_time = current_time
                if current_key_pressed == 1:
                    animation_phase = 2
                    animation_start_time = current_time
                    ack_frame_num = receiver.Rn % MAX_SEQ

                    ack_start_pos = (
                        receiver_start_x + ((receiver.Rn - 1) % MAX_SEQ) * 40 + 17,
                        receiver_start_y + 17
                    )
                    ack_end_pos = (
                        sender_start_x + ((receiver.Rn - 1) % MAX_SEQ) * 40 + 17,
                        sender_start_y + 17
                    )
                else:
                    animation_phase = 0

        elif animation_phase == 2:
            elapsed = current_time - animation_start_time
            if elapsed < animation_duration:
                progress = elapsed / animation_duration
                cur_x = ack_start_pos[0] + (ack_end_pos[0] - ack_start_pos[0]) * progress
                cur_y = ack_start_pos[1] + (ack_end_pos[1] - ack_start_pos[1]) * progress

                moving_rect = pygame.Rect(cur_x - 17, cur_y - 17, 35, 35)
                pygame.draw.rect(WINDOW, GREEN, moving_rect)
                frame_text = FONT.render(f"ACK{ack_frame_num}", True, BLACK)
                frame_text_rect = frame_text.get_rect(center=(cur_x, cur_y))
                WINDOW.blit(frame_text, frame_text_rect)
            else:
                sender.Sf = (sender.Sf + sender.cunt) % MAX_SEQ
                sender.cunt = 1
                message = f"Sender received ACK{ack_frame_num}. Sf incremented."
                message_time = current_time
                animation_phase = 0

        if message != "" and pygame.time.get_ticks() - message_time < 2000:
            display_info(message, (50, 550), RED)
        elif message != "" and pygame.time.get_ticks() - message_time >= 2000:
            message = ""

        instructions = [
            "Press 1: Send valid frame and ACK is sent.",
            "Press 2: Send corrupt frame.",
            "Press 3: Send valid frame but ACK is missing."
        ]
        for idx, instr in enumerate(instructions):
            display_info(instr, (50, 600 + idx * 25), BLUE)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
