import ActiveCompanies

comps = ActiveCompanies.active_companies()
english_names = list(comps.Name)



from nepali_unicode_converter.convert import Converter

converter = Converter()

for  name in english_names:
  print(converter.convert(name))