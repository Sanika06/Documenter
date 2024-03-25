from website import createApp
from flask import render_template
from flask import Flask, redirect, url_for

app = createApp()

if __name__ == ('__main__'):
    app.run(debug = True)
