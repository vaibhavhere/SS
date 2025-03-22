import win32com.client as win32

btApp = win32.Dispatch("BarTender.Application")
btApp.Visible = True


btFormat = btApp.Formats.Open("C:\\Users\\SS Auto\\Desktop\\SS.btw", False, "PrinterName")

btFormat.SetNamedSubStringValue("vehicle", "UNICORN")
btFormat.SetNamedSubStringValue("description", "DISC PAD")
btFormat.SetNamedSubStringValue("price", "250")

btFormat.IdenticalCopiesOfLabel = 1
#btFormat.PrintOut(False, False)
#btFormat.Close(1)
#btApp.Quit(1)