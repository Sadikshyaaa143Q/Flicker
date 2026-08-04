import pygame 
pygame.init()  # initialize the pygame module

screen=pygame.display.set_mode((800, 600))  # set the display window size to 800x600
pygame.display.set_caption("My button")  # set the window caption

font =pygame.font.Font('freesansbold.ttf', 32)  # set the font and size for the button text
surf=font.render('Quit', True, (255, 255, 255))  # render the button text with white color
button=pygame.Rect(300, 250, 200, 100)  # create a rectangle for the button at (300, 250) with width 200 and height 100
while True:
    screen.fill('pink')  # fill the screen with pink color
    for event in pygame.event.get():  # get all the events from the event queue
        if event.type==pygame.QUIT:  # check if the event is a quit event
            pygame.quit()  # quit pygame
        if event.type == pygame.MOUSEBUTTONDOWN:  # check if the event is a mouse button down event
            if button.collidepoint(event.pos):  # check if the mouse click is inside the button rectangle
                pygame.quit()  # quit pygame
                
    a,b=pygame.mouse.get_pos()  # get the current mouse position
    if button.x<= a <= button.x+button.width and button.y<= b <= button.y+button.height:  # check if the mouse is over the button
        pygame.draw.rect(screen, (180,180,180), button)
    else:
        pygame.draw.rect(screen, (110,110,110), button)  # draw the button rectangle with a different color if the mouse is not over it
    screen.blit(surf, (button.x+5, button.y+5))  
    pygame.display.update()  # update the display