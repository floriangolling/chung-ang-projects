	#include <ximage.h>
#include <iostream>
#include <string>

DWORD getFileFormat(std::string filePath)
{
	if (filePath.find('.jpg') != std::string::npos)
		return CXIMAGE_FORMAT_JPG;
	if (filePath.find('.PNG') != std::string::npos || filePath.find('.png') != std::string::npos)
		return CXIMAGE_FORMAT_PNG;
	if (filePath.find('.bmp') != std::string::npos)
		return CXIMAGE_FORMAT_BMP;
	return CXIMAGE_FORMAT_JPG;
}

int loadImages(const char* av[], CxImage* imageOne, CxImage* imageTwo, CxImage* imageThree)
{
	std::string currentPath = std::string(SOLUTION_DIR);
	std::string pathOne = currentPath + std::string(av[1]);
	std::string pathTwo = currentPath + std::string(av[2]);
	std::string pathThree = currentPath + std::string(av[3]);

	std::wstring pathOneByte = std::wstring(pathOne.begin(), pathOne.end());
	std::wstring pathTwoByte = std::wstring(pathTwo.begin(), pathTwo.end());
	std::wstring pathThreeByte = std::wstring(pathThree.begin(), pathThree.end());

	imageOne->Load(pathOneByte.c_str(), getFileFormat(pathOne));
	imageTwo->Load(pathTwoByte.c_str(), getFileFormat(pathTwo));
	imageThree->Load(pathThreeByte.c_str(), getFileFormat(pathThree));

	if (!imageOne->IsValid() || !imageTwo->IsValid() || !imageThree->IsValid())
		return 0;
	return 1;
}

char manageOverflow(int x) {
	return x > 255 || x < 0 ? x > 255 ? 255 : 0 : x;
}

void compositeFunction(CxImage* first, CxImage* second, bool type)
{
	DWORD width = first->GetWidth();
	DWORD height = first->GetHeight();
	RGBQUAD firstColor;
	RGBQUAD secondColor;
	RGBQUAD newColor;

	for (DWORD y = 0; y < height; y++) {
		for (DWORD x = 0; x < width; x++) {
			firstColor = first->GetPixelColor(x, y);
			secondColor = second->GetPixelColor(x, y);
			if (type) {
				newColor.rgbRed = (BYTE)(firstColor.rgbRed - secondColor.rgbRed < 0 ? 0 : firstColor.rgbRed - secondColor.rgbRed);
				newColor.rgbGreen = (BYTE)(firstColor.rgbGreen - secondColor.rgbGreen < 0 ? 0 : firstColor.rgbGreen - secondColor.rgbGreen);
				newColor.rgbBlue = (BYTE)(firstColor.rgbBlue - secondColor.rgbBlue < 0 ? 0 : firstColor.rgbBlue - secondColor.rgbBlue);
			}
			else {
				newColor.rgbRed = (BYTE)(firstColor.rgbRed + secondColor.rgbRed > 255 ? 255 : firstColor.rgbRed + secondColor.rgbRed);
				newColor.rgbGreen = (BYTE)(firstColor.rgbGreen + secondColor.rgbGreen > 255 ? 255 : firstColor.rgbGreen + secondColor.rgbGreen);
				newColor.rgbBlue = (BYTE)(firstColor.rgbBlue + secondColor.rgbBlue > 255 ? 255 : firstColor.rgbBlue + secondColor.rgbBlue);
			}
			first->SetPixelColor(x, y, newColor);
		}
	}
}

void processImages(CxImage* imageOne, CxImage* imageTwo, CxImage* imageThree)
{
	compositeFunction(imageOne, imageTwo, false);
	compositeFunction(imageOne, imageThree, true);
	std::string outputPath = std::string(SOLUTION_DIR) + std::string("output.PNG");
	std::wstring outputPathByte = std::wstring(outputPath.begin(), outputPath.end());
	imageOne->Save(outputPathByte.c_str(), CXIMAGE_FORMAT_PNG);
}

int main(int ac, const char *av[], char **envp)
{
	int returnValue = 0;
	CxImage *imageOne = new CxImage;
	CxImage *imageTwo = new CxImage;
	CxImage *imageThree = new CxImage;
	const char* defaultValues[4] = {
		NULL,
		"squid_body.PNG",
		"squid_head.PNG",
		"squid_points.PNG"
	};

	if (ac != 4) {
		returnValue = loadImages(defaultValues, imageOne, imageTwo, imageThree);
	} else {
		returnValue = loadImages(av, imageOne, imageTwo, imageThree);
	}

	processImages(imageOne, imageTwo, imageThree);
	free(imageOne);
	free(imageTwo);
	free(imageThree);
	if (!returnValue) {
		std::cout << "Files couldnt be opened, check you either have the good names, or enter different name in CLI." << std::endl;
		return -1;
	}
}