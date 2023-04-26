def start(prompt):
    out = ""
    for chunk in openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": prompt,
           
        }],
        stream=True,
        temperature= 0
    ):

        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            out += content
            print(content, end="")
    return out
  
  def animate_chalk(board, actions):
    outs = [draw_board(board.grid)]
    for action in actions:
        board, _ = board.move(action)
        outs.append(draw_board(board.grid))
    for i, v in enumerate(outs):
        v.render(f"pic{i}.png", 500)
    images = []
    for i in range(len(outs)):
        images.append(imageio.imread(f"pic{i}.png"))
    return imageio.mimsave('movie.gif', images, **{ 'duration': 0.5 })
    
animate_chalk(out.original, out.actions)
from IPython.display import Image
Image("movie.gif")  
