package main

import "github.com/codegangsta/martini"

func main() {
  m := martini.Classic()

  m.Use(martini.Static("/home/web/go.dajool.com/static"))

  m.Get("/", func() string {
    return "Hello world!"
  })

  m.Run()
}
