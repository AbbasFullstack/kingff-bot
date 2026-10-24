export default function handler(req, res) {
  res.status(200).json({
    files: ["bot.py - 331 lines Full", "requirements.txt", "README.md", "vercel-dashboard"],
    count: 4,
    time: new Date().toISOString()
  });
}
