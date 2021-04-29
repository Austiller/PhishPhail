import json
from pandas import DataFrame
from os import scandir, path


def main():



	try:


		filename = input("Drag and Drop file here:")

		fqdn = DataFrame.from_csv(filename)
		output = []

		for i in fqdn.index:
			row = {}
			row['model'] = "trainer.Brand"
			row['pk'] = i

			fields = {}
			for col in fqdn.columns:
				fields[col] = fqdn.loc[i][col].lower()

			#fields['forTraining'] = True

			row['fields'] = fields

			output.append(row)


		outputFile = input("Save As:")

		with open(outputFile,'w') as file:
			json.dump(output,file)
		

	except Exception:
		raise Exception


if __name__ == '__main__':
	main()