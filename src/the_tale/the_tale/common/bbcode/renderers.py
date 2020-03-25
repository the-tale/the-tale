
import smart_imports

smart_imports.all()


default = renderer.Renderer(tags=[tags.TAG.b,
                                  tags.TAG.i,
                                  tags.TAG.u,
                                  tags.TAG.s,
                                  tags.TAG.quote,
                                  tags.TAG.img,
                                  tags.TAG.url,
                                  tags.TAG.spoiler,
                                  tags.TAG.list,
                                  tags.TAG.list_id,
                                  tags.TAG.hr,
                                  tags.TAG.lsb,
                                  tags.TAG.rsb,
                                  tags.TAG.rl,
                                  tags.TAG.youtube,
                                  tags.TAG.center,
                                  tags.TAG.size,
                                  tags.TAG.color,
                                  tags.TAG.pre])

safe = renderer.Renderer(tags=[tags.TAG.b,
                               tags.TAG.i,
                               tags.TAG.u,
                               tags.TAG.s,
                               tags.TAG.quote,
                               tags.TAG.img,
                               tags.TAG.url,
                               tags.TAG.safe_spoiler,
                               tags.TAG.list,
                               tags.TAG.list_id,
                               tags.TAG.hr,
                               tags.TAG.lsb,
                               tags.TAG.rsb,
                               tags.TAG.rl])

chronicle = renderer.Renderer(tags=[tags.TAG.i,
                                    tags.TAG.url,
                                    tags.TAG.list,
                                    tags.TAG.list_id,
                                    tags.TAG.lsb,
                                    tags.TAG.rsb,
                                    tags.TAG.rl])
