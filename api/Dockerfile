FROM mcr.microsoft.com/dotnet/sdk:8.0

WORKDIR /app

COPY *.csproj .
RUN dotnet restore

# Source is mounted as a volume — do not COPY it
ENV DOTNET_USE_POLLING_FILE_WATCHER=1
CMD ["dotnet", "watch", "run", "--no-hot-reload"]
